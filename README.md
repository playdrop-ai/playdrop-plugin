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

## Local install

### Codex

Install this repository as a local plugin from source using the cloned repository root as the plugin path.

Then confirm the public skills are discoverable, starting with `playdrop:task-routing`.

### Claude Code

Install the plugin from the repository root:

```bash
claude --plugin-dir .
```

Then confirm the plugin and specialist skills are available, starting with `/playdrop` and `/playdrop:store-listing`.

### Cursor

Install this repository as a local plugin from source using the cloned repository root as the plugin path.

Then confirm the skills are discoverable, starting with `playdrop:task-routing`.

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
