# Changelog

## 1.0.7 — 2026-09-25

- Publish optional listing media with a game: icon, hero art, screenshots, a landscape trailer, a portrait teaser and
  localized art per language.
- Upload a Colyseus `server.js` to PlayDrop's free hosted game servers with MongoDB.
- Upload privately to test a version, then make it public from the game page.
- Test a game inside PlayDrop from your own dev server with `/dev?url=`.
- `get_documentation` accepts a topic (`overview`, `catalogue`, `sdk`, `server-sdk`) and returns current Markdown.
- New `send_feedback` tool sends questions, bugs and ideas to the PlayDrop team.
- The `playdrop-ai` skill now reads the latest documentation first and ships games in English plus your language.
- Each client folder has its own README, the icon is 512×512, and the repository lists the MCP Registry
  `server.json`.

## 1.0.6 — 2026-09-19

- Documented verified provider installs. Connection and skill unchanged from 1.0.5.

## 1.0.0–1.0.5 — 2026-09-19

- Replaced the former collection of game-development skills with one `playdrop-ai` publishing skill and a remote
  MCP connection with OAuth at `https://mcp.playdrop.ai/mcp`.
- Native packages for Codex, Claude Code, Antigravity and Grok Build, plus a portable Agent Plugins 1.0 package.
