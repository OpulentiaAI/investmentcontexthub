import assert from 'node:assert/strict'
import { test } from 'node:test'
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync, openSync, closeSync, realpathSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { spawn, execFileSync } from 'node:child_process'
import { setTimeout as delay } from 'node:timers/promises'

// Use the runtime's own broker and discovery; no package-local wire client.
test('native loading, map save and unchanged rerun',
  { skip: !process.env.AU_MCP_ROOT, timeout: 60000 }, async () => {
    const runtime = resolve(process.env.AU_MCP_ROOT)
    const { createEngineBroker } = await import(pathToFileURL(join(runtime, 'src/daemon/broker.ts')))
    const { discoverTools } = await import(pathToFileURL(join(runtime, 'src/daemon/discovery.ts')))
    const temporary = realpathSync(mkdtempSync(join(tmpdir(), 'research-map-')))
    const root = join(temporary, 'consumer')
    const packageRoot = fileURLToPath(new URL('..', import.meta.url))
    const put = (name, text) => { const path = join(root, name); mkdirSync(resolve(path, '..'), { recursive: true }); writeFileSync(path, text); return path }
    put('.arsumbris/repo.yaml', 'type: au.engine.repo::au-engine\nname: research-map-consumer\ndeps:\n  - name: au-tree-research\n')
    put('.arsumbris/workspace.yaml', 'type: au.engine.workspace::au-engine\nedit:\n  - research-map-consumer\n  - au-tree-research\n')
    const premise = put('premise - Field.md', '---\ntype: research-premise::au-tree-research\ntldr: Field\n---\n# Intent\nTest.\n# Out-of-scope\nOther work.\n')
    put('questions/q - What is the answer.md', '---\ntype: question.researched::au-tree-research\ntldr: First question\nprompt: What is the answer?\nparent: "[[premise - Field]]"\n---\n')
    put('articles/Answer.md', '---\ntype: article::au-tree-research\ntldr: Answer summary\nanswers: "[[q - What is the answer]]"\n---\n# Overview\nThe answer.\n')
    put('questions/q - What follows.md', '---\ntype: question.open::au-tree-research\ntldr: Follow-up\nprompt: What follows?\nparent: "[[q - What is the answer]]"\n---\n')
    const git = (...args) => execFileSync('git', ['-C', root, ...args], { encoding: 'utf8' }).trim()
    git('init', '-q'); git('add', '.'); git('-c', 'user.name=Map tests', '-c', 'user.email=map@localhost', 'commit', '-qm', 'fixture')
    const log = join(temporary, 'daemon.log'), fd = openSync(log, 'w')
    const daemon = spawn('au', ['daemon', 'start', root], { stdio: ['ignore', fd, fd] })
    closeSync(fd)
    const broker = createEngineBroker(root)
    try {
      let ready = false
      for (let i = 0; i < 100; i++) {
        try { ready = (await broker.read('lifecycle')).ready === true } catch {}
        if (ready || daemon.exitCode !== null) break
        await delay(100)
      }
      assert.ok(ready, readFileSync(log, 'utf8'))
      const discovery = await discoverTools(broker, { workspace: root, broker }, id => id !== 'mcp.refresh_research_map')
      const tool = discovery.loaded.find(p => p.manifest.id === 'mcp.refresh_research_map')
      assert.ok(tool, 'native loader must load the package tool')
      assert.equal(discovery.provenances.get(tool.manifest.id), 'au-tree-research')
      assert.deepEqual(discovery.inputSchemas.get(tool.manifest.id).required, ['premise'])
      assert.equal(discovery.inputSchemas.get(tool.manifest.id).properties.dry_run.type, 'boolean')
      const members = (await broker.read('members')).result
      assert.equal(resolve(members.find(m => m.repo === 'au-tree-research').root), resolve(packageRoot), 'exercise current working copy')
      const invoke = async (input = {}) => {
        const result = await tool.invoke({ premise, ...input }, {})
        assert.equal(result.isError, undefined, result.content)
        return JSON.parse(result.content)
      }
      const before = git('rev-parse', 'HEAD')
      const saved = await invoke()
      assert.equal(saved.status, 'saved')
      assert.equal(saved.path, join(root, 'map - Field.md'))
      assert.equal(readFileSync(saved.path, 'utf8').split('# Index\n\n')[1], '- [[premise - Field]]\n  - [[Answer]]\n    - [[q - What follows]]\n')
      assert.deepEqual((await broker.read('diagnostics', { path: saved.path, severity: 'error' })).result, [])
      const commit = git('rev-parse', 'HEAD')
      assert.notEqual(commit, before)
      assert.equal((await invoke()).status, 'unchanged')
      assert.equal(git('rev-parse', 'HEAD'), commit)
    } finally {
      broker.close()
      try { execFileSync('au', ['daemon', 'stop', root], { stdio: 'ignore', timeout: 10000 }) } catch {}
      if (daemon.exitCode === null) { daemon.kill('SIGTERM'); await Promise.race([new Promise(r => daemon.once('exit', r)), delay(3000)]); }
      if (daemon.exitCode === null) daemon.kill('SIGKILL')
      rmSync(temporary, { recursive: true, force: true })
    }
  })
