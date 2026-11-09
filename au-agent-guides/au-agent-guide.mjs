// File-guide discovery uses the current broker's unwrapped read payloads.
// Request resolved instances so body-authored goal/rule/about fields reach the index.
import { basename, extname, isAbsolute } from 'node:path'

const GUIDE_TYPE = 'guide::au-agent-guides'
const INDEX_FIELDS = ['goal', 'rule', 'about']

function messageOf(error) {
  return error instanceof Error ? error.message : String(error ?? 'unknown error')
}

function failure(message) {
  return { content: message, isError: true }
}

async function readPayload(broker, op, args, label) {
  let frame
  try {
    frame = await broker.read(op, args)
  } catch (error) {
    throw new Error(label + ' failed: ' + messageOf(error))
  }
  if (frame?.type === 'error') {
    throw new Error(label + ' failed: ' + (frame.message ?? 'unspecified engine error'))
  }
  if (frame?.ready === false) {
    throw new Error('The engine is still building the workspace. Try again in a moment.')
  }
  if (frame?.ready !== true) {
    throw new Error(label + ' returned a malformed broker frame (missing readiness).')
  }
  return frame.result
}

function parseSelector(input = {}) {
  if (input === null || typeof input !== 'object' || Array.isArray(input)) {
    throw new Error('Use an object: {}, {name: "guide-name"}, or {path: "<indexed absolute path>"}.')
  }
  if (Object.keys(input).some((key) => key !== 'name' && key !== 'path')) {
    throw new Error('Only name or path is supported. Omit both to list guides.')
  }
  const hasName = Object.hasOwn(input, 'name')
  const hasPath = Object.hasOwn(input, 'path')
  if (hasName && hasPath) throw new Error('Supply either name or path, not both.')
  if (!hasName && !hasPath) return { kind: 'index' }
  const value = input[hasName ? 'name' : 'path']
  if (typeof value !== 'string' || !value.trim()) {
    throw new Error('The selector must be a nonempty string. Use {} to list guides.')
  }
  if (hasPath) {
    if (!isAbsolute(value)) throw new Error('Use the exact absolute path shown in the guide index.')
    return { kind: 'path', path: value }
  }
  const parts = value.trim().split('::').map((part) => part.trim())
  if (parts.length > 2 || parts.some((part) => !part)) {
    throw new Error('Use name or name::package with a nonempty name and package.')
  }
  return { kind: 'name', name: parts[0], member: parts[1] }
}

// Index text summarizes routing fields; the selected guide is always served verbatim.
// Conflicting or invalid values stay visible instead of silently choosing one.
function renderValue(field, value) {
  if (value?.kind === 'scalar' && typeof value.value === 'string') {
    return JSON.stringify(value.value)
  }
  if (field === 'about' && value?.kind === 'reference' && typeof value.target === 'string') {
    return JSON.stringify(value.target + (value.repo ? '::' + value.repo : ''))
  }
  return '[invalid ' + field + ' value; inspect source and diagnostics]'
}

function toEntry(row, index) {
  const malformed = () => new Error('The guide index returned a malformed row at position ' + (index + 1) + '.')
  if (
    !row || typeof row.path !== 'string' || !isAbsolute(row.path) ||
    row.origin !== 'file' || typeof row.member !== 'string' || !row.member ||
    !Array.isArray(row.claim) || row.claim.length === 0 ||
    !row.claim.every((claim) => typeof claim === 'string' && claim.length > 0) ||
    !Array.isArray(row.instance?.effective_values)
  ) throw malformed()

  const summaries = []
  for (const field of INDEX_FIELDS) {
    const groups = row.instance.effective_values.filter((group) => group?.field === field)
    const values = []
    for (const group of groups) {
      if (!Array.isArray(group.containers)) throw malformed()
      for (const container of group.containers) {
        if (!container?.value || typeof container.value !== 'object') throw malformed()
        values.push(renderValue(field, container.value))
      }
    }
    if (values.length) {
      const conflict = values.length > 1 ? '[' + values.length + ' values; inspect diagnostics] ' : ''
      summaries.push(field + ': ' + conflict + values.join(' | '))
    }
  }
  const name = basename(row.path, extname(row.path))
  if (!name) throw malformed()
  return { name, member: row.member, path: row.path, claims: row.claim, summaries }
}

async function readIndex(broker) {
  const rows = await readPayload(
    broker, 'instances_of',
    { type: GUIDE_TYPE, origins: ['file'], instance: true },
    'The guide index query',
  )
  if (!Array.isArray(rows)) throw new Error('The guide index returned a malformed payload (expected an array).')
  const byPath = new Map()
  rows.forEach((row, index) => {
    const entry = toEntry(row, index)
    const previous = byPath.get(entry.path)
    if (previous && JSON.stringify(previous) !== JSON.stringify(entry)) {
      throw new Error('The guide index returned conflicting rows for ' + JSON.stringify(entry.path) + '.')
    }
    byPath.set(entry.path, entry)
  })
  // Code-point ordering keeps the same index independent of the process locale.
  const compare = (a, b) => a < b ? -1 : a > b ? 1 : 0
  return [...byPath.values()].sort((a, b) =>
    compare(a.name, b.name) || compare(a.member, b.member) || compare(a.path, b.path))
}

function qualifiedName(entry) {
  return entry.name + '::' + entry.member
}

function renderIndex(entries) {
  if (entries.length === 0) {
    return 'No file guides currently match guide::au-agent-guides in the mounted workspace.'
  }
  const lines = [
    'Ars Umbris guides from the mounted workspace.',
    'Select by {name: "name::package"} or by the exact {path: "..."} shown below.',
    'A bare name works when unique. Use path when names also collide within one package.',
    'Goal, rule, and about summarize resolved fields; claims show the authored type names.',
    '',
  ]
  for (const entry of entries) {
    lines.push('- ' + JSON.stringify(qualifiedName(entry)))
    lines.push('    path: ' + JSON.stringify(entry.path))
    lines.push('    claims: ' + entry.claims.map((claim) => JSON.stringify(claim)).join(', '))
    lines.push(...entry.summaries.map((summary) => '    ' + summary))
  }
  return lines.join('\n')
}

function selectEntry(entries, selector) {
  const matches = entries.filter((entry) =>
    selector.kind === 'path' ? entry.path === selector.path :
      entry.name === selector.name && (!selector.member || entry.member === selector.member))
  if (matches.length === 0) {
    throw new Error('No indexed guide matches that selector. Call with {} to list current names and paths.')
  }
  if (matches.length > 1) {
    const options = matches.map((entry) =>
      '  ' + JSON.stringify({ name: qualifiedName(entry) }) + '; exact selection: ' + JSON.stringify({ path: entry.path }))
    throw new Error(
      'The guide name is ambiguous. Qualify by package, or use {path: "<exact source path>"} ' +
      'when a qualified name still collides. Matches:\n' + options.join('\n'),
    )
  }
  return matches[0]
}

async function serveOne(broker, entry) {
  const content = await readPayload(broker, 'content', { path: entry.path }, 'Reading ' + qualifiedName(entry))
  if (typeof content?.text !== 'string') {
    throw new Error('The guide content returned a malformed payload (expected text).')
  }
  return {
    content: 'Guide: ' + JSON.stringify(qualifiedName(entry)) +
      '\nSource: ' + JSON.stringify(entry.path) +
      '\nResolve relative links from this source file.\n\n' + content.text,
  }
}

/** @param {{ broker?: { available?: () => boolean, read: Function } }} ctx */
export function createPlugin(ctx) {
  const broker = ctx?.broker
  return {
    invoke: async (input) => {
      try {
        const selector = parseSelector(input)
        if (!broker || typeof broker.read !== 'function' ||
          (typeof broker.available === 'function' && !broker.available())) {
          return failure('The guide broker is unavailable. This tool needs broker: read and a running engine daemon.')
        }
        const entries = await readIndex(broker)
        if (selector.kind === 'index') return { content: renderIndex(entries) }
        return await serveOne(broker, selectEntry(entries, selector))
      } catch (error) {
        return failure(messageOf(error))
      }
    },
  }
}
