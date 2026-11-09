import { basename, dirname, isAbsolute, join, relative, sep } from 'node:path'
import { existsSync } from 'node:fs'

const type = name => `${name}::au-tree-research`
const identity = value => `${value.name}:${value.hash}`
const inside = (root, path) => { const rel = relative(root, path); return !isAbsolute(rel) && rel !== '..' && !rel.startsWith(`..${sep}`) }
const badQualification = new Set(['mixin-collision', 'mixed-bare-and-qualified-field', 'malformed-qualifier-key',
  'qualifier-not-in-closure', 'qualifier-does-not-declare-field', 'qualifier-ambiguous'])

// Select the research contract's contributions, including qualified consumer fields.
async function fields(instance, contract, repo, closure) {
  if (instance.diagnostics?.some(d => badQualification.has(d.code))) throw Error('Invalid field qualification; resolve engine diagnostics first.')
  const scoped = name => name.includes('::') ? name : `${name}::${repo}`
  const origins = new Map((await closure(type(contract))).fields.map(f => [f.name, identity(f.origin)]))
  const members = new Set()
  for (const claim of instance.claim) for (const a of (await closure(scoped(claim))).ancestors) members.add(identity(a))
  const selected = new Map()
  for (const entry of instance.effective_values) {
    const key = /^([^{}]+)(?:\{([^{}]+)\})?$/.exec(entry.field)
    if (!key || !origins.has(key[1])) continue
    for (const container of entry.containers) {
      const contributions = []
      let qualified = false
      for (const contribution of container.contributions) {
        const q = contribution.qualifier
        const qualifier = q ? q.type_name + (q.repo ? `::${q.repo}` : '') : key[2]
        if (qualifier) {
          const c = await closure(scoped(qualifier))
          if (!members.has(identity(c.identity)) || !c.ancestors.some(a => identity(a) === origins.get(key[1]))) continue
        }
        contributions.push(contribution)
        qualified ||= !!qualifier
      }
      if (contributions.length) {
        if (!selected.has(key[1])) selected.set(key[1], [])
        selected.get(key[1]).push({ ...container, contributions, qualified })
      }
    }
  }
  return selected
}

function target(containers = [], edges, field) {
  const targets = new Set()
  for (const c of containers) {
    const stringLink = c.qualified && c.value.kind === 'scalar' && /^\[\[[^\[\]\n]+\]\]$/.test(c.value.value)
    if (c.value.kind !== 'reference' && !stringLink) return null
    for (const contribution of c.contributions) {
      const span = contribution.location.byte_range
      const matches = edges.filter(e => e.field?.split('{')[0] === field &&
        (['field-reference', 'contributing'].includes(e.kind) || (stringLink && e.kind === 'field-string-wikilink')) &&
        span.start <= e.span.start && e.span.end <= span.end)
      if (!matches.length || matches.some(e => !e.resolved || e.commit || e.block_id?.referent)) return null
      for (const e of matches) targets.add(e.resolved)
    }
  }
  return targets.size === 1 ? [...targets][0] : null
}

function replaceIndex(instance, text, index) {
  const headings = (instance.body_events ?? []).filter(e => e.kind === 'heading' && e.level === 1).sort((a, b) => a.span.start - b.span.start)
  const indexes = headings.filter(e => e.text === 'Index')
  if (indexes.length !== 1) throw Error('Map needs exactly one top-level Index section; nothing written.')
  const raw = Buffer.from(text)
  const start = indexes[0].span.end
  const end = headings.find(e => e.span.start > indexes[0].span.start)?.span.start ?? raw.length
  if (!(0 <= start && start <= end && end <= raw.length)) throw Error('Invalid engine section spans.')
  for (const f of instance.effective_values) for (const c of f.containers) for (const contribution of c.contributions) {
    const span = contribution.location.byte_range
    if (span.start < end && span.end > start) throw Error(`Index contributes to ${f.field}; move that value outside Index first.`)
  }
  const prefix = raw.subarray(0, start).toString()
  const suffix = raw.subarray(end).toString()
  return prefix + (prefix.endsWith('\n') ? '\n' : '\n\n') + index + (suffix ? '\n' : '') + suffix
}

export function createPlugin({ broker }) {
  return { async invoke(input) {
    let writing
    try {
      if (!input || !isAbsolute(input.premise ?? '') || (input.dry_run !== undefined && typeof input.dry_run !== 'boolean')) throw Error('Supply an absolute premise path and optional boolean dry_run.')
      if (!broker?.available()) throw Error('The engine broker is unavailable.')
      // Hold one graph version across reads. A busy field fails without retrying writes.
      let version
      async function read(op, args = {}) {
        const frame = await broker.read(op, args)
        if (frame.type === 'error' || frame.ready !== true || !Number.isInteger(frame.version)) throw Error(`Engine ${op} failed: ${frame.message ?? 'not ready or missing graph version'}`)
        version ??= frame.version
        if (frame.version !== version) throw Error('Graph changed during refresh; rerun after research finishes.')
        return frame.result
      }
      const member = (await read('members')).filter(m => m.root && inside(m.root, input.premise)).sort((a, b) => b.root.length - a.root.length)[0]
      if (!member?.local || !member.editable) throw Error('Premise must belong to a local editable member.')
      const closures = new Map()
      async function closure(name) {
        if (!closures.has(name)) {
          const rows = await read('type_closure', { name })
          if (rows.length !== 1) throw Error(`Cannot resolve one type identity for ${name}.`)
          closures.set(name, rows[0])
        }
        return closures.get(name)
      }
      const notes = new Map()
      for (const kind of ['research-premise', 'question.open', 'question.researched', 'question.dropped', 'article', 'map.computed-index']) {
        for (const row of await read('instances_of', { type: type(kind), origins: ['file'], instance: true })) {
          if (row.member !== member.repo) continue
          if (notes.has(row.path)) throw Error(`Conflicting research roles at ${row.path}.`)
          notes.set(row.path, { ...row, kind })
        }
      }
      if (notes.get(input.premise)?.kind !== 'research-premise') throw Error('The path is not a research premise.')
      const children = new Map(), answers = new Map(), maps = []
      const warnings = []
      const append = (map, key, value) => { if (!map.has(key)) map.set(key, []); map.get(key).push(value) }
      for (const note of [...notes.values()].sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0)) {
        if (!note.instance?.resolved) throw Error(`Unresolved research instance at ${note.path}.`)
        const contract = note.kind.startsWith('question.') ? 'question' : note.kind
        const values = await fields(note.instance, contract, member.repo, closure)
        const field = contract === 'question' ? 'parent' : contract === 'article' ? 'answers' : contract === 'map.computed-index' ? 'premise' : null
        if (!field) continue
        note.target = target(values.get(field), await read('references_out', { path: note.path }), field)
        if (!note.target) warnings.push(`${note.path}: ${field} is not one resolved live file reference; omitted.`)
        if (contract === 'question' && note.kind !== 'question.dropped') append(children, note.target, note)
        if (contract === 'article') append(answers, note.target, note)
        if (contract === 'map.computed-index' && note.target === input.premise) maps.push(note)
      }
      if (maps.length > 1) throw Error('Multiple maps bind this premise; nothing written.')
      const existing = maps[0]
      const premiseStem = basename(input.premise).replace(/\.[^.]+$/, '')
      const fieldName = premiseStem.replace(/^premise - /, '') || premiseStem
      const path = existing?.path ?? join(dirname(input.premise), `map - ${fieldName}.md`)
      const old = await read('content', { path })
      if (!existing && (old !== null || existsSync(path))) throw Error(`Map destination already exists: ${path}`)
      if (existing && (!old || typeof old.text !== 'string' || !old.hash)) throw Error(`Cannot read map content and hash: ${path}`)
      async function link(note) {
        // Ask from the actual output origin; never infer identity from a basename.
        for (const candidate of [basename(note.path).replace(/\.[^.]+$/, ''), relative(member.root, note.path).split(sep).join('/')]) {
          if ((await read('resolve_target', { target: candidate, origin: path }))?.path === note.path) return `[[${candidate}]]`
        }
        throw Error(`Cannot produce an unambiguous link for ${note.path}.`)
      }
      const lines = [`- §0 ${await link(notes.get(input.premise))}`], visited = new Set(), stack = [[notes.get(input.premise), 1]]
      const numbering = []
      while (stack.length) {
        const [note, depth] = stack.pop()
        if (visited.has(note.path)) throw Error(`Cycle or repeated question at ${note.path}.`)
        visited.add(note.path)
        let childDepth = depth
        if (note.kind.startsWith('question.')) {
          const articles = answers.get(note.path) ?? []
          if (note.kind === 'question.open' && articles.length) warnings.push(`${note.path}: open question has an article; review before completing.`)
          if (note.kind === 'question.researched' && !articles.length) warnings.push(`${note.path}: researched question has no article.`)
          const labels = note.kind === 'question.open' ? [await link(note)] : []
          for (const article of articles) {
            const sections = article.instance.section_presence
            const overview = sections ? sections.some(s => s.name === 'Overview' && s.depth === 1 && s.present) :
              article.instance.body_events?.some(e => e.kind === 'heading' && e.level === 1 && e.text === 'Overview')
            labels.push(await link(article))
            if (!overview) warnings.push(`${article.path}: no Overview; review the article.`)
          }
          if (labels.length) {
            // The open question and any answers share one subject and descendants.
            numbering[depth - 1] = (numbering[depth - 1] ?? 0) + 1
            numbering.length = depth
            lines.push(`${'  '.repeat(depth)}- §${numbering.join('.')} ${labels.join(' · ')}`)
            childDepth++
          }
        }
        for (const child of [...(children.get(note.path) ?? [])].reverse()) stack.push([child, childDepth])
      }
      const index = `${lines.join('\n')}\n`
      const content = existing ? replaceIndex(existing.instance, old.text, index) :
        `---\ntype: map.computed-index::au-tree-research\ntldr: ${JSON.stringify('Computed map of the ' + fieldName + ' tree.')}\npremise: ${JSON.stringify(await link(notes.get(input.premise)))}\n---\n\n# Index\n\n${index}`
      const result = { path, status: input.dry_run ? 'preview' : old?.text === content ? 'unchanged' : 'saved', warnings }
      if (input.dry_run) result.preview = content
      if (result.status === 'saved') {
        if (!existing && ((await read('content', { path })) !== null || existsSync(path))) throw Error(`Map destination appeared: ${path}`)
        await read('lifecycle')
        writing = path
        const frame = await broker.mutate('write_file', { path, content, ...(old ? { expected_hash: old.hash } : {}) })
        if (frame.type === 'error' || frame.ready !== true) throw Error(frame.message ?? 'Engine write failed.')
        if (frame.result?.reflected !== true) throw Error('Engine has not confirmed the saved map in its graph.')
        if (frame.result.diagnostics?.some(d => d.severity === 'error')) throw Error(`Map saved with diagnostics: ${JSON.stringify(frame.result.diagnostics)}`)
        writing = undefined
      }
      return { content: JSON.stringify(result) }
    } catch (error) {
      return { content: `${error.message}${writing ? ` Inspect ${writing} before rerunning; the write may have landed.` : ''}`, isError: true }
    }
  } }
}
