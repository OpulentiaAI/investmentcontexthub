import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createPlugin } from '../refresh-research-map.mjs'

const root = '/map-test'
const qualify = name => `${name}::au-tree-research`
const id = name => ({ name, hash: name })
const contribution = { location: { byte_range: { start: 0, end: 1 } } }
function row(path, kind, parent) {
  const field = kind.startsWith('question.') ? 'parent' : kind === 'article' ? 'answers' : 'premise'
  const values = [{ field: 'tldr', containers: [{ value: { kind: 'scalar', value: path }, contributions: [contribution] }] }]
  if (parent) values.push({ field, containers: [{ value: { kind: 'reference' }, contributions: [contribution] }] })
  return { path: `${root}/${path}.md`, member: 'consumer', kind, parent: parent && `${root}/${parent}.md`, field,
    instance: { claim: [qualify(kind)], resolved: true, effective_values: values, body_events: [] } }
}
function fixture() {
  const rows = [row('Field', 'research-premise'), row('q', 'question.open', 'Field'),
    row('child', 'question.researched', 'q'), row('Answer', 'article', 'q'),
    row('Dropped', 'question.dropped', 'Field'), row('Hidden', 'question.open', 'Dropped'),
    row('Other', 'research-premise'), row('Elsewhere', 'question.open', 'Other')]
  rows.find(r => r.kind === 'article').instance.body_events = [{ kind: 'heading', level: 1, text: 'Overview' }]
  const writes = [], contents = new Map()
  const broker = {
    available: () => true,
    async read(op, args) {
      let result
      switch (op) {
        case 'members': result = [{ repo: 'consumer', root, local: true, editable: true }]; break
        case 'type_closure': {
          const kind = args.name.split('::')[0], contract = kind.startsWith('question.') ? 'question' : kind
          result = [{ identity: id(kind), ancestors: [id(kind), id(contract)], fields: ['tldr', 'parent', 'answers', 'premise'].map(name => ({ name, origin: id(contract) })) }]; break
        }
        case 'instances_of': result = rows.filter(r => qualify(r.kind) === args.type); break
        case 'references_out': {
          const r = rows.find(r => r.path === args.path)
          result = r.parent ? [{ field: r.field, kind: 'field-reference', resolved: r.parent, span: { start: 0, end: 1 } }] : []; break
        }
        case 'content': result = contents.get(args.path) ?? null; break
        case 'resolve_target': result = { path: `${root}/${args.target}.md` }; break
        case 'lifecycle': result = {}; break
        default: throw Error(`Unexpected read ${op}`)
      }
      return { ready: true, version: 1, result }
    },
    async mutate(op, args) { writes.push({ op, ...args }); return { ready: true, result: { reflected: true, diagnostics: [] } } },
  }
  return { broker, rows, writes, contents, invoke: input => createPlugin({ broker }).invoke({ premise: `${root}/Field.md`, ...input }) }
}

const indexOf = preview => preview.split('# Index\n\n')[1]

test('new maps sit beside the premise and omit its filename prefix', async () => {
  const f = fixture()
  f.rows.splice(0, f.rows.length, row('premise - Field', 'research-premise'))
  const response = await f.invoke({ premise: `${root}/premise - Field.md`, dry_run: true })
  assert.equal(response.isError, undefined, response.content)
  assert.equal(JSON.parse(response.content).path, `${root}/map - Field.md`)
  assert.equal(indexOf(JSON.parse(response.content).preview), '- §0 [[premise - Field]]\n')
})

test('open questions and articles render, closed questions stay hidden and incomplete work warns', async () => {
  const f = fixture()
  f.rows.push(row('Hidden answer', 'article', 'Hidden'), row('Other answer', 'article', 'Elsewhere'))
  const response = await f.invoke({ dry_run: true })
  assert.equal(response.isError, undefined, response.content)
  const { preview, warnings, status } = JSON.parse(response.content)
  assert.equal(status, 'preview')
  assert.equal(JSON.parse(response.content).path, `${root}/map - Field.md`)
  assert.equal(indexOf(preview), '- §0 [[Field]]\n  - §1 [[q]] · [[Answer]]\n')
  assert.equal(warnings.length, 2)
  assert.equal(f.writes.length, 0)
})

test('descendants nest under open questions and articles', async () => {
  const f = fixture()
  f.rows.push(row('gap', 'question.open', 'q'), row('deep', 'question.researched', 'gap'),
    row('Deep answer', 'article', 'deep'), row('child answer', 'article', 'child'),
    row('sibling', 'question.researched', 'Field'), row('Sibling answer', 'article', 'sibling'))
  const response = await f.invoke({ dry_run: true })
  assert.equal(response.isError, undefined, response.content)
  assert.equal(indexOf(JSON.parse(response.content).preview),
    '- §0 [[Field]]\n  - §1 [[q]] · [[Answer]]\n    - §1.1 [[child answer]]\n    - §1.2 [[gap]]\n      - §1.2.1 [[Deep answer]]\n  - §2 [[Sibling answer]]\n')
})

test('multiple answers share one row with descendants below the group', async () => {
  const f = fixture()
  f.rows.push(row('Alternative', 'article', 'q'), row('Child answer', 'article', 'child'))
  const response = await f.invoke({ dry_run: true })
  assert.equal(response.isError, undefined, response.content)
  assert.equal(indexOf(JSON.parse(response.content).preview),
    '- §0 [[Field]]\n  - §1 [[q]] · [[Alternative]] · [[Answer]]\n    - §1.1 [[Child answer]]\n')
})

test('a field with no articles still shows its open questions', async () => {
  const f = fixture()
  f.rows.splice(f.rows.findIndex(r => r.kind === 'article'), 1)
  const response = await f.invoke({ dry_run: true })
  assert.equal(response.isError, undefined, response.content)
  assert.equal(indexOf(JSON.parse(response.content).preview), '- §0 [[Field]]\n  - §1 [[q]]\n')
})

function existing(f, text) {
  const map = row('Map', 'map.computed-index', 'Field')
  map.instance.body_events = [...text.matchAll(/^# (Index|Notes)[^\r\n]*(?:\r?\n|$)/gm)].map(m => ({
    kind: 'heading', level: 1, text: m[1],
    span: { start: Buffer.byteLength(text.slice(0, m.index)), end: Buffer.byteLength(text.slice(0, m.index + m[0].length)) },
  }))
  f.rows.push(map)
  f.contents.set(map.path, { text, hash: 'read-hash' })
  return map
}

test('updates preserve authored content and refuse stale writes', async () => {
  const f = fixture()
  const prefix = '---\r\nowner: Zoë\r\n---\r\n# Index ^keep\r\n'
  const suffix = '# Notes\r\nKeep café.\r\n'
  existing(f, prefix + '\r\nOld index\r\n\r\n' + suffix)
  const response = await f.invoke()
  assert.equal(response.isError, undefined, response.content)
  assert.equal(JSON.parse(response.content).path, `${root}/Map.md`)
  assert.ok(f.writes[0].content.startsWith(prefix))
  assert.ok(f.writes[0].content.endsWith(suffix))
  assert.equal(f.writes[0].expected_hash, 'read-hash')
  let attempts = 0
  f.broker.mutate = async () => { attempts++; return { type: 'error', message: 'stale hash' } }
  const rejected = await f.invoke()
  assert.equal(rejected.isError, true)
  assert.match(rejected.content, /stale hash/)
  assert.equal(attempts, 1)
})
