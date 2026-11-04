# PlayDrop Agent Plugin

[![Release](https://img.shields.io/github/v/release/playdrop-ai/playdrop-plugin)](https://github.com/playdrop-ai/playdrop-plugin/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Publish, test and share the browser games you build with your AI agent on [PlayDrop](https://www.playdrop.ai).
Want PlayDrop to build and maintain the game for you instead? Start with [PlayDrop Cloud](https://www.playdrop.ai/create).

The plugin adds one skill, `playdrop-ai`, and a connection to PlayDrop's remote MCP server at
`https://mcp.playdrop.ai/mcp`. Sign in to your PlayDrop account through OAuth; there is no CLI or package to install.

The public PlayDrop CLI and legacy CLI-based skills are retired. Publish games through the
[PlayDrop connector](https://www.playdrop.ai/create/connectors).

## Install

- **Claude Code:** `/plugin marketplace add playdrop-ai/playdrop-plugin`, then `/plugin install playdrop@playdrop`.
  Sign in with `/mcp` → `plugin:playdrop:playdrop` → Authenticate, then run `/playdrop:publish` in your game project.
- **Codex:** `codex plugin marketplace add playdrop-ai/playdrop-plugin`, then install PlayDrop from the Plugins Directory.
- **Grok Build:** `grok plugin install 'playdrop-ai/playdrop-plugin#variants/grok/playdrop' --trust`.
- **Antigravity:** clone this repository, then `agy plugin install ./playdrop-plugin/variants/antigravity/playdrop`.
- **Replit:** [add PlayDrop to Replit](https://replit.com/integrations?mcp=eyJkaXNwbGF5TmFtZSI6IlBsYXlEcm9wIEFJIiwiYmFzZVVybCI6Imh0dHBzOi8vbWNwLnBsYXlkcm9wLmFpL21jcCJ9).
- **Gemini web, iOS and Android:** add a custom app on [Gemini web](https://gemini.google.com), then use the same
  Google account on mobile. Requires an eligible personal US account, age 18+, English and Keep Activity enabled.
  See the [Gemini guide](https://www.playdrop.ai/create/connectors/gemini); consumer runtime validation is pending.
- **ChatGPT, Claude, Lovable, Grok and other MCP clients:** add a custom connector with the URL
  `https://mcp.playdrop.ai/mcp` and OAuth.

[PlayDrop Connector](https://www.playdrop.ai/create/connectors) has a step-by-step guide for each platform:

- Agents with plugins: [Codex](https://www.playdrop.ai/create/connectors/codex),
  [Claude Code](https://www.playdrop.ai/create/connectors/claude-code),
  [Antigravity](https://www.playdrop.ai/create/connectors/antigravity).
- Hosted assistants: [ChatGPT](https://www.playdrop.ai/create/connectors/chatgpt),
  [Claude](https://www.playdrop.ai/create/connectors/claude), [Lovable](https://www.playdrop.ai/create/connectors/lovable),
  [Replit](https://www.playdrop.ai/create/connectors/replit), [Grok](https://www.playdrop.ai/create/connectors/grok),
  [Gemini](https://www.playdrop.ai/create/connectors/gemini).

[Installation](INSTALLATION.md) covers each package in detail, with dated compatibility results.

## What your agent can do

- Publish one self-contained HTML game up to 10 MiB with `upload_game`, or a built folder, ZIP or `.play` package
  with [catalogue.json](https://www.playdrop.ai/create/learn/packaging) for several files, listing art and video,
  PlayDrop SDK features and hosted servers. Your source project stays with you; PlayDrop receives built output.
- Choose who can play: private for testing, unlisted for anyone with the link, or public for discovery. Release a
  tested private version with `publish_game_version`, and update the same game later without changing its link.
- Reach players on the web and in PlayDrop's iOS, Android, Windows and macOS apps, where games play full screen.
- Add [cloud saves](https://www.playdrop.ai/create/learn/cloud-saves),
  [leaderboards](https://www.playdrop.ai/create/learn/leaderboards), sharing and invites,
  [online parties with voice](https://www.playdrop.ai/create/learn/online-party), gamepads and phone controllers,
  [hosted Colyseus servers with MongoDB](https://www.playdrop.ai/create/learn/game-servers), and optional tips,
  purchases and ads that earn the creator credits.
- Test a running local game inside PlayDrop before uploading: open
  `https://www.playdrop.ai/@<username>/<slug>/dev?url=http%3A%2F%2Flocalhost%3A5173%2F` in a browser on the machine
  that runs the local server. The Extensions panel provides Live/Draft playback of uploaded versions.
- Send questions, bugs and ideas to the PlayDrop team with the feedback tool.

Your agent reads the current guides with `get_documentation`: `{topic:"index"}` lists them all. The same guides are
on the web at [playdrop.ai/create/learn](https://www.playdrop.ai/create/learn), in 20 languages.

## Contents

- `plugin.json`, `mcp.json`, `skills/`: portable Agent Plugins 1.0 package.
- `plugins/playdrop/`: Codex native package with its registered public OAuth client.
- `variants/claude/playdrop/`: Claude Code native package with its registered public OAuth client.
- `variants/antigravity/playdrop/`, `variants/grok/playdrop/`: native client packages.
- `.agents/plugins/`, `.claude-plugin/`, `.grok-plugin/`: repository marketplace metadata.
- `server.json`: the [MCP Registry](https://registry.modelcontextprotocol.io) entry, `ai.playdrop/mcp`.

All packages point at the URL in `mcp.json`; generated development copies may point at a development service.
Version 1.0 replaced the older broad game-development plugin with one publishing skill and a remote connection.
This MIT-licensed package contains no server implementation or credentials. Never add access tokens to it.
