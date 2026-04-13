# playdrop-plugin

Canonical public PlayDrop plugin source for Codex, Claude Code, and Cursor.

This repository is the source of truth for the public `playdrop` plugin. It contains the plugin manifests, public creator-facing skills, shared references, and shared assets used to support PlayDrop creator workflows.

## Public links

- Home page: [playdrop.ai](https://www.playdrop.ai/)
- Getting Started: [playdrop.ai/getting-started](https://www.playdrop.ai/getting-started)
- Plugin docs: [playdrop.ai/docs/plugin](https://www.playdrop.ai/docs/plugin)
- Full documentation: [playdrop.ai/docs](https://www.playdrop.ai/docs)

## Repository layout

- `.codex-plugin/`: Codex manifest
- `.claude-plugin/`: Claude manifest
- `.cursor-plugin/`: Cursor manifest
- `skills/`: specialist public PlayDrop skills
- `references/`: shared public workflow references
- `assets/`: plugin icons and branding assets

## Install the Plugin

### Codex

Use this exact local Codex setup:

1. Copy the plugin repo into:

```text
~/.codex/plugins/playdrop
```

2. Create or update:

```text
~/.agents/plugins/marketplace.json
```

with:

```json
{
  "name": "local-plugins",
  "interface": {
    "displayName": "Local Plugins"
  },
  "plugins": [
    {
      "name": "playdrop",
      "source": {
        "source": "local",
        "path": "./.codex/plugins/playdrop"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Coding"
    }
  ]
}
```

3. Restart Codex so it reloads the personal marketplace.
4. Open `Plugins > Local Plugins`, then install `playdrop` from `local-plugins`.
5. Start a new thread and ask Codex to use `playdrop` or one of its bundled skills.

Optional advanced shortcut for personal setups:

```toml
[plugins."playdrop@local-plugins"]
enabled = true
```

Add that entry to `~/.codex/config.toml` if you want Codex to keep the plugin enabled after it has been installed. Treat it as a local shortcut for your own machine, not the primary install path. If PlayDrop does not appear, use the restart plus `Plugins > Local Plugins` flow above.

### Claude Code

Either run these commands in Claude CLI directly, or tell the Claude app to run them with Claude CLI.

```bash
/plugin marketplace add playdrop-ai/playdrop-plugin
/plugin install playdrop@playdrop
```

`/plugin` is not available inside the Claude Code app at the moment.

### Cursor

Copy this prompt into Cursor to register the plugin:

```text
Install the PlayDrop Cursor Plugin from https://github.com/playdrop-ai/playdrop-plugin in ~/.cursor/plugins/local/
Source: https://cursor.com/docs/plugins#creating-plugins
```

## Validation

Use short representative checks instead of treating discovery alone as sufficient.

- Codex: verify `playdrop:task-routing`, `playdrop:game-planning`, `playdrop:scope-control`, and `playdrop:store-listing`
- Claude Code: verify `/playdrop`, `/playdrop:game-planning`, `/playdrop:scope-control`, and `/playdrop:store-listing`
- Cursor: verify `playdrop:task-routing`, `playdrop:game-planning`, `playdrop:scope-control`, and `playdrop:store-listing`
- Workflow smoke tests:
  - `game-planning` -> `scope-control` -> `gameplay-mockups`
  - `dev-testing` -> `gameplay-review` -> `store-listing`
  - `project-updates` -> `service-integration`
  - `engine-porting` -> `dev-testing`

## Versioning

Plugin manifests in this repository are on the same release train as the PlayDrop platform and must match the platform version. Version alignment and legacy sync are maintained from the private PlayDrop monorepo.

## Legacy sync

`playdrop-skills` is a generated compatibility, skills.sh, and SEO surface. It is not the source of truth.

Run the sync from the private PlayDrop monorepo root:

```bash
node scripts/sync-legacy-skills-repo.mjs
```

Check for drift with:

```bash
node scripts/sync-legacy-skills-repo.mjs --check
```

Align the public plugin manifests with the platform release version from the monorepo:

```bash
node scripts/set-public-plugin-version.mjs 0.6.2
```
