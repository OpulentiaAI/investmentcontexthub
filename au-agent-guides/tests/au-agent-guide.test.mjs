import assert from 'node:assert/strict'
import test from 'node:test'
import { createPlugin } from '../au-agent-guide.mjs'

// Shapes taken from the current engine-sdk WireInstanceMatch and WireFieldValues.
// The au-mcp broker unwraps instances_of and content before the plugin sees them.
const scalar = (value) => ({ kind: 'scalar', value })
const reference = (target, repo) => ({ kind: 'reference', target, repo, anchor: null, block_id: null })
const field = (name, ...values) => ({
  field: name, containers: values.map((value) => ({ value, contributions: [] })),
})
const row = (path = '/packages/one/guides/choose.md', member = 'one', values = []) => ({
  path, member, origin: 'file', claim: ['guide::au-agent-guides'],
  fields: {}, name: 'guide', type_owners: ['au-agent-guides'],
  instance: { resolved: true, effective_values: values },
})
const ready = (result) => ({ type: 'response', ready: true, result })

function fixture(rows = [row()], sources = {}, overrides = {}) {
  const calls = []
  const broker = {
    available: () => true,
    read: async (op, args) => {
      calls.push({ op, args })
      if (overrides.read) return overrides.read(op, args)
      if (op === 'instances_of') return ready(rows)
      if (op === 'content') return ready({ text: sources[args.path] ?? 'guide body\n', hash: 'abc', commit: 'def' })
      throw new Error('Unexpected operation: ' + op)
    },
    ...Object.fromEntries(Object.entries(overrides).filter(([key]) => key !== 'read')),
  }
  return { calls, invoke: createPlugin({ broker }).invoke }
}

test('indexes resolved body fields and authored custom claims across packages', async () => {
  const guide = row('/packages/peer/notes/choose.md', 'peer', [
    field('goal', scalar('Choose from body\nwith a second line')),
    field('rule', scalar('The body supplies the rule.')),
    field('about', reference('mcp.tool', 'au-mcp-sdk')),
  ])
  guide.fields = { goal: null, rule: 'raw frontmatter is not the effective value' }
  guide.claim = ['decision-advice::peer', 'audited::peer']
  const f = fixture([guide])
  const result = await f.invoke({})
  assert.equal(result.isError, undefined)
  assert.match(result.content, /choose::peer/)
  assert.match(result.content, /Choose from body\\nwith a second line/)
  assert.match(result.content, /The body supplies the rule/)
  assert.match(result.content, /about: "mcp.tool::au-mcp-sdk"/)
  assert.match(result.content, /claims: "decision-advice::peer", "audited::peer"/)
  assert.doesNotMatch(result.content, /raw frontmatter/)
  assert.deepEqual(f.calls, [{
    op: 'instances_of',
    args: { type: 'guide::au-agent-guides', origins: ['file'], instance: true },
  }])
})

test('supports about-only and fieldless guides without inventing required metadata', async () => {
  const f = fixture([
    row('/packages/one/about.yaml', 'one', [field('about', reference('local-contract'))]),
    row('/packages/one/empty.md'),
  ])
  const result = await f.invoke()
  assert.equal(result.isError, undefined)
  assert.match(result.content, /about::one/)
  assert.match(result.content, /about: "local-contract"/)
  assert.match(result.content, /empty::one/)
  assert.doesNotMatch(result.content, /goal:|rule:/)
})

test('makes conflicting or invalid routing fields visible without discarding the guide', async () => {
  const f = fixture([row(undefined, undefined, [
    field('goal', scalar('first'), scalar('second')),
    field('rule', scalar(false)),
  ])])
  const result = await f.invoke({})
  assert.match(result.content, /2 values; inspect diagnostics/)
  assert.match(result.content, /"first" \| "second"/)
  assert.match(result.content, /invalid rule value/)
  assert.equal((await f.invoke({ name: 'choose' })).isError, undefined)
})

for (const [label, source] of [
  ['LF', '---\ntype: guide\ngoal: Frontmatter matters\n---\n\n# Body\n\nText.\n\n'],
  ['CRLF and BOM', '\uFEFF---\r\ntype: guide\r\n---\r\n\r\nBody\r\n'],
  ['frontmatter only', '---\ntype: guide\nrule: The entire answer.\n---'],
  ['empty concurrent content', ''],
]) {
  test('serves the complete source unchanged: ' + label, async () => {
    const path = '/packages/one/nested/choose.md'
    const f = fixture([row(path)], { [path]: source })
    const result = await f.invoke({ name: 'choose' })
    assert.equal(result.isError, undefined)
    assert.match(result.content, /^Guide: "choose::one"\nSource: "\/packages\/one\/nested\/choose.md"/)
    assert.match(result.content, /Resolve relative links from this source file/)
    assert.equal(result.content.slice(result.content.indexOf('\n\n') + 2), source)
    assert.deepEqual(f.calls.at(-1), { op: 'content', args: { path } })
  })
}

test('reads the source fresh on every invocation', async () => {
  let version = 0
  const f = fixture(undefined, undefined, {
    read: (op) => op === 'instances_of' ? ready([row()]) : ready({ text: 'version ' + (++version) }),
  })
  assert.match((await f.invoke({ name: 'choose' })).content, /version 1$/)
  assert.match((await f.invoke({ name: 'choose' })).content, /version 2$/)
})

test('distinguishes cross-package collisions and accepts a qualified name', async () => {
  const f = fixture([row(), row('/packages/two/guides/choose.md', 'two')])
  const ambiguous = await f.invoke({ name: 'choose' })
  assert.equal(ambiguous.isError, true)
  assert.match(ambiguous.content, /choose::one/)
  assert.match(ambiguous.content, /choose::two/)
  assert.equal(f.calls.filter(({ op }) => op === 'content').length, 0)
  const selected = await f.invoke({ name: ' choose::two ' })
  assert.equal(selected.isError, undefined)
  assert.match(selected.content, /Source: "\/packages\/two\/guides\/choose.md"/)
})

test('resolves a same-package basename collision by exact indexed path', async () => {
  const second = '/packages/one/other/choose.md'
  const f = fixture([row(), row(second)])
  const ambiguous = await f.invoke({ name: 'choose::one' })
  assert.equal(ambiguous.isError, true)
  assert.match(ambiguous.content, /exact selection/)
  assert.match(ambiguous.content, /\/other\/choose.md/)
  const selected = await f.invoke({ path: second })
  assert.equal(selected.isError, undefined)
  assert.match(selected.content, /Source: "\/packages\/one\/other\/choose.md"/)
})

test('unknown selectors never become arbitrary content reads', async () => {
  const f = fixture()
  for (const input of [{ name: 'absent' }, { name: 'choose::absent' }, { path: '/private/secret.md' }]) {
    assert.equal((await f.invoke(input)).isError, true)
  }
  assert.equal(f.calls.filter(({ op }) => op === 'content').length, 0)
})

test('rejects malformed selectors before querying the broker', async () => {
  const f = fixture()
  for (const input of [
    null, [], 'choose', { name: 42 }, { name: '' }, { path: ' ' }, { name: '::one' },
    { name: 'choose::' }, { name: 'choose::one::two' }, { path: 'relative.md' },
    { name: 'choose', path: '/packages/one/guides/choose.md' }, { unexpected: true },
  ]) {
    assert.equal((await f.invoke(input)).isError, true, JSON.stringify(input))
  }
  assert.equal(f.calls.length, 0)
})

test('deduplicates identical paths and sorts deterministically', async () => {
  const a = row('/packages/one/z.md')
  const b = row('/packages/two/a.md', 'two')
  const c = row('/packages/one/a.md')
  const f = fixture([a, b, c, structuredClone(a)])
  const result = await f.invoke({})
  assert.equal(result.content.match(/^- /gm).length, 3)
  assert.ok(result.content.indexOf('a::one') < result.content.indexOf('a::two'))
  assert.ok(result.content.indexOf('a::two') < result.content.indexOf('z::one'))
  assert.equal((await f.invoke({ name: 'z' })).isError, undefined)
})

test('reports inconsistent duplicate rows', async () => {
  const conflicting = row()
  conflicting.member = 'different-owner'
  const f = fixture([row(), conflicting])
  assert.match((await f.invoke({})).content, /conflicting rows/)
  assert.equal((await f.invoke({})).isError, true)
})

test('distinguishes an empty index from unavailable, unready, or malformed data', async () => {
  const empty = await fixture([]).invoke({})
  assert.equal(empty.isError, undefined)
  assert.match(empty.content, /^No file guides currently match/)
  for (const frame of [
    { type: 'response', ready: false },
    { type: 'response', result: [] },
    ready({ instances_of: [] }), // The broker already unwraps this envelope.
    ready(null),
    ready([null]),
    ready([{ ...row(), instance: undefined }]),
    ready([{ ...row(), origin: 'nested' }]),
    ready([{ ...row(), path: 'relative.md' }]),
    ready([row(undefined, undefined, [{ field: 'goal', containers: null }])]),
  ]) {
    const f = fixture(undefined, undefined, { read: () => frame })
    const result = await f.invoke({})
    assert.equal(result.isError, true, JSON.stringify(frame))
    assert.doesNotMatch(result.content, /^No file guides/)
  }
})

test('returns SDK error results when the broker is missing or unavailable', async () => {
  for (const ctx of [{}, { broker: {} }, { broker: { read() {}, available: () => false } }]) {
    const result = await createPlugin(ctx).invoke({})
    assert.equal(result.isError, true)
    assert.match(result.content, /broker is unavailable/)
  }
})

for (const stage of ['index', 'content']) {
  for (const kind of ['engine error', 'transport error', 'malformed content', 'unready']) {
    test('reports ' + kind + ' during ' + stage, async () => {
      const f = fixture(undefined, undefined, {
        read: (op) => {
          if (stage === 'content' && op === 'instances_of') return ready([row()])
          if (kind === 'engine error') return { type: 'error', message: 'precise engine failure' }
          if (kind === 'transport error') throw new Error('socket disconnected')
          if (kind === 'unready') return { type: 'response', ready: false }
          return ready({ text: 123 })
        },
      })
      const result = await f.invoke(stage === 'index' ? {} : { name: 'choose' })
      assert.equal(result.isError, true)
      if (kind === 'engine error') assert.match(result.content, /precise engine failure/)
      if (kind === 'transport error') assert.match(result.content, /socket disconnected/)
      if (kind === 'unready') assert.match(result.content, /still building/)
      if (kind === 'malformed content') assert.match(result.content, /malformed payload/)
    })
  }
}
