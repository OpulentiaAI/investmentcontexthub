# au-defaults

Starter workspaces and shared bundles for Ars Umbris. The host discovers this repository through the device's `workspace-template-repos.yaml`, reads `workspace-templates.yaml` before starting the graph, and preserves its order.

The gallery offers **Blank**, **Deep research**, **Weave** and **Arscontexta (experimental)**. Names, descriptions, highlights and illustrated layout previews are authored in that manifest. Previews describe the intended layout; they are not runtime screenshots.

Creating a workspace copies the selected folder into a new user-owned folder. The host renames the repo identity and workspace self-reference, registers the copy, and materializes the manifest's `initialComposition` as a typed `workspace-startup.yaml` reference. Compositions, keymaps, guides and profiles travel with the copy. A valid remembered composition takes precedence on subsequent visits.

Every listed starter includes a standard shell, a guide in the Reader, and Claude Code and Codex profiles. Authentication and device connection settings remain separate; templates contain no credentials or live sessions. Blank is the general app starting point; the other starters add the packages and guidance described in their gallery metadata.

## Bundles and installation

- `host-bundle` supplies the host projection and vocabulary closure.
- `mcp-bundle` supplies agent vocabulary and both adapters.

Workspaces consume bundles through `discover:`. Bundle `deps` declare their members; declarations do not fetch or install packages. Installation must locate the complete dependency closure in the engine device registry and register this template repository in the host device config. Optional extra members in the launcher come from that device registry.
