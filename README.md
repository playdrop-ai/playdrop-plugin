# PlayDrop Agent Plugin

Upload, update and share public HTML games from your AI agent through PlayDrop's remote MCP.
Version 1.0 replaces the older broad game-development plugin with one publishing skill and a remote connection.
The backend is operated separately; this MIT-licensed package contains no server implementation or credentials.

**Rollout status — September 19, 2026:** version 1.0 is published in this repository for the server rollout.
The matching MCP/OAuth server changes are awaiting deployment and production acceptance.
Public directory availability and a working connection in every provider are not yet established.

## Contents

- `plugin.json`, `mcp.json`, `skills/`: portable Agent Plugins 1.0 package.
- `plugins/playdrop/`: Codex native package with its registered public OAuth client.
- `variants/claude/playdrop/`: Claude Code native package with its registered public OAuth client.
- `variants/antigravity/playdrop/`, `variants/grok/playdrop/`: native client packages.
- `.agents/plugins/`, `.claude-plugin/`, `.grok-plugin/`: repository marketplace metadata.
- [Installation and provider submission](INSTALLATION.md): choose one package per agent.

All packages point at the URL in `mcp.json`. Generated development copies may point at a development service.
The production endpoint is `https://mcp.playdrop.ai/mcp`.
Sign in to your PlayDrop account when the client requests OAuth. Never add access tokens to this repository.

## Requirements and status

PlayDrop requires MCP `2026-07-28` with stateless HTTPS. There are no stdio, old-protocol or SSE bridges.
A supported package format does not prove that the installed client supports this MCP protocol version.
Provider OAuth, publication, updates and large-file transport must pass acceptance testing before support is claimed.
Codex 0.153.4 passed browser OAuth, reads, game creation/update and exact 5 MiB publication in development.
ChatGPT and Claude custom connectors passed browser OAuth, reads and game creation/update in development.
Claude Code 2.1.270 passed native plugin browser OAuth, reads and tiny-game creation/update in development.
Antigravity 1.2.7 passed native plugin reads using fixture OAuth.
Grok Build 1.0.34 passed strict discovery with seven tools using fixture OAuth.
Remaining provider-specific OAuth and publication checks are described in [installation guidance](INSTALLATION.md).

Publishing requires a single `index.html` plus catalogue metadata. Both upload paths publish publicly:
content in tool arguments, or a signed file upload followed by explicit MCP completion.
Read the connected server's documentation for current quotas, limits and fields.
The plugin does not edit Studio projects or install a local PlayDrop CLI.

## Package check

```sh
node tools/validate-package.mjs .
```

This checks package contents and configuration offline. It does not authenticate, publish a game or verify a provider.
