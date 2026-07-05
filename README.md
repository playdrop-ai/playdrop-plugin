# playdrop-plugin

Canonical public PlayDrop plugin source for Codex, Claude Code, and Cursor.

This repository is the source of truth for the public `playdrop` plugin. It contains the plugin manifests, public creator-facing skills, shared references, and shared assets used to support PlayDrop creator workflows.

## Public links

- Home page: [playdrop.ai](https://www.playdrop.ai/)
- Getting Started: [playdrop.ai/getting-started](https://www.playdrop.ai/getting-started)
- Plugin docs: [playdrop.ai/docs/plugin](https://www.playdrop.ai/docs/plugin)
- Full documentation: [playdrop.ai/docs](https://www.playdrop.ai/docs)

## Repository layout

- `.agents/plugins/`: Codex marketplace manifest
- `.codex-plugin/`: Codex manifest
- `.claude-plugin/`: Claude manifest
- `.cursor-plugin/`: Cursor manifest
- `skills/`: specialist public PlayDrop skills
- `references/`: shared public workflow references
- `assets/`: plugin icons and branding assets
- `plugins/playdrop`: compatibility symlink used by marketplace catalogs that require plugin sources below the repository root

## Install the Plugin

### Codex

Install or update the PlayDrop marketplace through the Codex CLI:

```bash
codex plugin marketplace add playdrop-ai/playdrop-plugin
codex plugin add playdrop@playdrop
```

Refresh the marketplace snapshot before reinstalling or verifying an update:

```bash
codex plugin marketplace upgrade playdrop
codex plugin add playdrop@playdrop
codex plugin list
```

### Claude Code

Either run these commands in Claude CLI directly, or tell the Claude app to run them with Claude CLI.

```bash
/plugin marketplace add playdrop-ai/playdrop-plugin
/plugin install playdrop@playdrop
```

`/plugin` is not available inside the Claude Code app at the moment.

### Cursor

Install the plugin from the Cursor marketplace or import this repository as a team marketplace. For local testing, copy or symlink this repository into:

```text
~/.cursor/plugins/local/playdrop
```

then restart Cursor or run `Developer: Reload Window`.

## Validation

Use short representative checks instead of treating discovery alone as sufficient.

- Codex: verify `playdrop:task-routing`, `playdrop:create-game`, `playdrop:update-game`, `playdrop:remix-game`, and `playdrop:make-listing`
- Claude Code: verify `/playdrop`, `/playdrop:create-game`, `/playdrop:update-game`, and `/playdrop:make-listing`
- Cursor: verify `playdrop:task-routing`, `playdrop:create-game`, `playdrop:update-game`, `playdrop:remix-game`, and `playdrop:make-listing`
- Marketing: verify `playdrop:make-listing` and `playdrop:market-game`
- Workflow smoke tests:
  - `create-game` -> `discover-assets` -> `make-assets` -> `playtest-game` -> `make-listing`
  - `remix-game` -> `playtest-game` -> `make-listing`
  - `update-game` -> `playtest-game` -> `make-listing`
  - `review-game` with the staged game-review references

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
