# PlayDrop Agent Plugin

Upload, update and share public HTML games from your AI agent through PlayDrop's remote MCP.
Version 1.0 replaces the older broad game-development plugin with one publishing skill and a remote connection.
The backend is operated separately; this MIT-licensed package contains no server implementation or credentials.

**Rollout status — September 19, 2026:** the production MCP and OAuth endpoint are live.
ChatGPT, Claude, Codex, Claude Code, Antigravity, Lovable, Replit and Grok hosted chat passed production reads
and game creation/update. Codex also passed a signed 5 MiB upload and completion replay. Provider listings remain
unsubmitted; installing this package does not imply a reviewed listing or support in every client.

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

The matching server supports stateless HTTPS MCP `2026-07-28` and Streamable HTTP revisions
`2025-03-26`, `2025-06-18` and `2025-11-25` through one endpoint and the same OAuth/tools.
Older initialization is supported without MCP sessions; POST responses can be JSON or bounded SSE.
GET/DELETE remain unavailable. There is no separate HTTP+SSE endpoint or stdio bridge.
A supported package format does not by itself establish client compatibility.
Provider OAuth, publication, updates and large-file transport must pass acceptance testing before support is claimed.
Grok Build passed OAuth, reads and creation/update in development; production OAuth remains unverified.
Grok Bot and Gemini have account eligibility gates; Muse runtime testing remains unverified.
Cursor needs the prepared OAuth callback fix deployed and retested. Locally built iOS and Android apps played
SDK-free production fixtures; those native readiness fixes still need app releases.
See [installation guidance](INSTALLATION.md) for setup, dated evidence and remaining account gates.

Publishing requires a single `index.html` plus catalogue metadata. Both upload paths publish publicly:
content in tool arguments, or a signed file upload followed by explicit MCP completion.
Read the connected server's documentation for current quotas, limits and fields.
The plugin does not edit Studio projects or install a local PlayDrop CLI.

## Package check

```sh
node tools/validate-package.mjs .
```

This checks package contents and configuration offline. It does not authenticate, publish a game or verify a provider.
