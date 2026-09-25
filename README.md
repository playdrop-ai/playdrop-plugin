# PlayDrop Agent Plugin

[![Release](https://img.shields.io/github/v/release/playdrop-ai/playdrop-plugin)](https://github.com/playdrop-ai/playdrop-plugin/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Publish, test and share the browser games you build with your AI agent on [PlayDrop](https://www.playdrop.ai).
Want PlayDrop to build and maintain the game for you instead? Start with [PlayDrop Cloud](https://www.playdrop.ai/create).

The plugin adds one skill, `playdrop-ai`, and a connection to PlayDrop's remote MCP server at
`https://mcp.playdrop.ai/mcp`. Sign in to your PlayDrop account when your agent asks; there is no CLI or package to
install.

## Install

- **Claude Code:** `/plugin marketplace add playdrop-ai/playdrop-plugin`, then `/plugin install playdrop@playdrop`.
- **Codex:** `codex plugin marketplace add playdrop-ai/playdrop-plugin`, then install PlayDrop from the Plugins Directory.
- **Grok Build:** `grok plugin install 'playdrop-ai/playdrop-plugin#variants/grok/playdrop' --trust`.
- **Antigravity:** clone this repository, then `agy plugin install ./playdrop-plugin/variants/antigravity/playdrop`.
- **Replit:** [add PlayDrop to Replit](https://replit.com/integrations?mcp=eyJkaXNwbGF5TmFtZSI6IlBsYXlEcm9wIEFJIiwiYmFzZVVybCI6Imh0dHBzOi8vbWNwLnBsYXlkcm9wLmFpL21jcCJ9).
- **ChatGPT, Claude, Lovable, Grok and other MCP clients:** add a custom connector with the URL
  `https://mcp.playdrop.ai/mcp` and OAuth.

[PlayDrop Connector](https://www.playdrop.ai/docs/connectors) has a step-by-step guide for each platform:

- Agents with plugins: [Codex](https://www.playdrop.ai/docs/connectors/codex),
  [Claude Code](https://www.playdrop.ai/docs/connectors/claude-code),
  [Antigravity](https://www.playdrop.ai/docs/connectors/antigravity).
- Hosted assistants: [ChatGPT](https://www.playdrop.ai/docs/connectors/chatgpt),
  [Claude](https://www.playdrop.ai/docs/connectors/claude), [Lovable](https://www.playdrop.ai/docs/connectors/lovable),
  [Replit](https://www.playdrop.ai/docs/connectors/replit), [Grok](https://www.playdrop.ai/docs/connectors/grok).

[Installation](INSTALLATION.md) covers each package in detail, with dated compatibility results.

## What your agent can do

- Publish `index.html` with its [catalogue.json](https://www.playdrop.ai/docs/catalogue-json) metadata, plus an
  optional icon, hero art, screenshots, a landscape trailer and a portrait teaser, localized per language.
- Upload privately to test a version, then make it public from the game page. Update the same game later.
- Test inside PlayDrop before publishing:
  `https://www.playdrop.ai/creators/<username>/apps/game/<slug>/dev?url=http://localhost:5173/`.
- Add the optional [client SDK](https://www.playdrop.ai/docs/sdk) with one script tag: leaderboards, achievements,
  cloud saves, social features and multiplayer.
- Run multiplayer on your own server, or upload a [Colyseus](https://colyseus.io) `server.js` to PlayDrop's free hosted
  game servers with [MongoDB](https://www.mongodb.com). See [game servers](https://www.playdrop.ai/docs/server-sdk).
- Send questions, bugs and ideas to the PlayDrop team with the feedback tool.

Your agent reads current limits and formats with `get_documentation`. Everything is also at
[playdrop.ai/docs](https://www.playdrop.ai/docs).

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

## Package check

```sh
node tools/validate-package.mjs .
```

This checks package contents and configuration offline. It does not authenticate, publish a game or verify a provider.
