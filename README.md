# PlayDrop Agent Plugin

Create, upload, publish and manage web games on PlayDrop. Use the optional PlayDrop SDK for advanced features and online services.

This repository is a generated public distribution. Do not commit changes directly because the next publication will replace them. Open bug reports and feature requests in the [issue tracker](https://github.com/playdrop-ai/playdrop-plugin/issues).

The plugin follows the [Agent Plugins 1.0 specification](https://agent-plugins.org/specification) and works with compatible clients including ChatGPT, Codex, Cursor, and VS Code. Claude Code metadata is included separately because Claude currently uses its own plugin manifest and community marketplace.

## Public links

- Home page: [playdrop.ai](https://www.playdrop.ai/)
- Getting Started: [playdrop.ai/getting-started](https://www.playdrop.ai/getting-started)
- Plugin docs: [playdrop.ai/docs/plugin](https://www.playdrop.ai/docs/plugin)
- Tweaks docs: [playdrop.ai/docs/creator-tools/tweaks](https://www.playdrop.ai/docs/creator-tools/tweaks)
- Playtest Notes docs: [playdrop.ai/docs/creator-tools/playtest-notes](https://www.playdrop.ai/docs/creator-tools/playtest-notes)
- Full documentation: [playdrop.ai/docs](https://www.playdrop.ai/docs)

## Repository layout

- `plugin.json`: portable Agent Plugins manifest
- `skills/`: specialist public PlayDrop skills
- `references/`: shared public workflow references
- `.claude-plugin/`: Claude Code compatibility and marketplace metadata
- `.agents/plugins/`: Codex repository marketplace catalog, which is distribution metadata rather than a plugin-format manifest
- `assets/`: plugin icons and branding assets
- `tools/validate-plugin.mjs`: dependency-free portable manifest and skill validation
- `tools/validate-submission.mjs`: end-to-end public artifact and marketplace preflight
- `submission/marketplaces.json`: machine-readable listing metadata and review cases
- `MARKETPLACE_SUBMISSION.md`: copy-ready submission materials and owner actions

## Install the Plugin

### Codex

Install or update the PlayDrop repository marketplace through the Codex CLI:

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

Install the plugin from the Cursor marketplace. Cursor reads the root Agent Plugins manifest directly. For local testing, copy or symlink this repository into:

```text
~/.cursor/plugins/local/playdrop
```

then restart Cursor or run `Developer: Reload Window`.

## Validation

Validate the portable package from the repository root:

```bash
node tools/validate-plugin.mjs
node tools/validate-submission.mjs .
claude plugin validate --strict .
```

Use short representative checks instead of treating discovery alone as sufficient.

- Codex: verify `playdrop:create-game`, `playdrop:phaser-2d-game`, `playdrop:three-js-game`, `playdrop:update-game`, `playdrop:tweaks`, `playdrop:playtest-notes`, `playdrop:remix-game`, `playdrop:make-2d-asset-pack`, and `playdrop:make-listing`
- Claude Code: verify `/playdrop`, `/playdrop:create-game`, `/playdrop:update-game`, and `/playdrop:make-listing`
- Cursor: verify `playdrop:create-game`, `playdrop:update-game`, `playdrop:remix-game`, and `playdrop:make-listing`
- Marketing: verify `playdrop:market-game`, `playdrop:make-marketing-screenshots`, `playdrop:make-marketing-video`, and `playdrop:make-social-media-package`
- Workflow smoke tests:
  - `create-game` -> new, remix, or update guidance -> relevant capabilities -> `playtest-game` -> `make-listing`
  - `discover-assets` -> `make-assets` -> `make-2d-asset-pack` when transparent generated art is needed

## Versioning

The portable and Claude manifests use the same release version. Publication is automated and direct commits to this generated mirror are frozen.

## Legacy sync

The separate `playdrop-skills` repository remains a generated compatibility, skills.sh, SEO, and discovery surface. This plugin repository is the canonical public package to install.
