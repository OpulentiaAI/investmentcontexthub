---
type: guide
goal: "Build a native agent tool from its definition and executable entry."
rule: "Define the input and typed metadata, implement createPlugin, then verify discovery, advertised schema, and invocation."
about: "[[mcp.tool::au-mcp-sdk]]"
example:
---

# Build a loadable tool

Build the tool from:

- A subtype of [[mcp.tool::au-mcp-sdk]]
- Typed metadata
- An executable module

Name the definition `mcp.tool.<name>`.
The current loader filters by that prefix as well as inheritance.
Another name can validate while being omitted from discovery.

Use [[scaffold-a-package]] for identity and dependencies.
First-party core tools use this package mechanism too.

**Declare input and runtime metadata**

Read the current metadata contracts:

- [[plugin-runtime-meta::au-mcp-sdk]]
- [[tool-presentation-meta::au-mcp-sdk]]
- [[tool-access-meta::au-mcp-sdk]]

- Fields describe input
- Runtime metadata locates the module relative to its owner and declares the plugin contract version
- Presentation supports selection
- Access scopes the supplied broker

A tool has no hook shapes.
Callable is not a shape value.

**Implement the entry contract**

Read [[mcp.tool.au_agent_guide::au-agent-guides:example]] and its linked entry module.
Its ESM exports createPlugin(ctx), which returns an invoke function.
Invoke returns a CallableResult with content and isError on failure.

Use the SDK types for TypeScript.
Choose the build and dependencies the runtime needs.
A pure tool can still need package.json.

**Handle mutations deliberately**

Use the provided broker and supported engine mutation contract.
Read current state and preserve its concurrency token.
Handle rejection and uncertain outcomes.
A successful write can leave diagnostics.
Inspect the outcome before retrying after a lost response.

**Trace a call through the loader**

Check the definition and required metadata.
Then inspect qualified subtype discovery.
Refresh the daemon and adapter as needed to load code and advertise its schema.
Invoke representative success and failure cases.

Follow a call from advertised arguments through the loaded module to the returned result.
A clean definition alone does not establish loading or working behavior.
