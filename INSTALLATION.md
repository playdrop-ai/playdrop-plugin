# Installing and submitting PlayDrop

These are packaging instructions with dated development checks below.
Packaging validation, MCP protocol acceptance and browser OAuth onboarding are separate checks.
Select one package per client; do not install the portable and native variants together.
For development, use the generated package's endpoint instead of production in every provider form.
As of September 19, 2026, the public 1.0.3 source is prepared for rollout; matching server deployment and production
acceptance remain pending. Repository publication does not enable a provider directory listing.

## Packages

| Client | Package or connection | Discovery/public listing |
| --- | --- | --- |
| ChatGPT / Codex | Portable root; Codex fallback `plugins/playdrop` | Optional public directory review |
| Claude | Custom connector using endpoint and OAuth | Optional connector directory review |
| Claude Code | `variants/claude/playdrop` | Repo marketplace; public directory is separate |
| Gemini | Custom MCP is unavailable to the tested work account | Account eligibility gate |
| Antigravity | `variants/antigravity/playdrop` | Manual install; curated store is separate |
| Grok Bot | Paid-plan access required on the tested account; runtime unverified | Separate from hosted chat and Build |
| Grok hosted chat | Custom HTTPS connector and OAuth; reads/create/update passed locally | Private connection first |
| Grok Build | `variants/grok/playdrop` | Repo marketplace, no public listing required |
| Cursor | Previous strict-endpoint failure requires retesting | Cloud agent access also needs a paid plan |
| Lovable | Custom MCP URL and OAuth; reads/create/update passed locally | No listing required for private connection |
| Replit | Personal MCP URL and OAuth; reads/create/update passed locally | Public discovery is separate |
| Muse | Submit an Existing MCP connector with endpoint and OAuth PKCE | Review required for directory listing |

The portable format has no OAuth client-ID field. Its connection uses client discovery and whatever registration
method the server offers. Native Codex and Claude packages retain their public client IDs; other clients require
server-side OAuth onboarding or discovery support. Credentials and tokens are never packaged.

## Local installation

Codex: add this local repository as a marketplace using `codex plugin marketplace add /path/to/repository`.
Its `.agents/plugins/marketplace.json` selects the native Codex fallback. Install PlayDrop in the client UI.
Claude Code: use `/plugin marketplace add /path/to/repository`, then `/plugin install playdrop@playdrop`.
Antigravity: `agy plugin install /path/to/repository/variants/antigravity/playdrop`.
Grok Build: `grok plugin install /path/to/repository/variants/grok/playdrop --trust` after reviewing the package.
These commands change local client state; the package build does not run them.
Antigravity 1.2.7 and Grok Build 1.0.34 validate their native variants with one skill and one MCP server.
Their validators detect only the skill in the portable root; use the native variants on those versions.

Codex 0.153.4 was tested with `mcp_2026_07_28`; Claude Code 2.1.270 with `MCP_SDK_GENERATION=v2`.
Codex passed native browser OAuth, account/game reads, create/update and exact 5 MiB publishing in development.
Claude Code passed native plugin browser OAuth, documentation/account/game reads, and tiny-game create/update.
Antigravity 1.2.7 passed native plugin DCR/browser OAuth, reads and game create/update.
Grok Build 1.0.34 passed browser OAuth, reads and game create/update using its native HTTP configuration.
Its plugin validation passed separately; the write run did not establish execution through the installed plugin.
These write checks verified the updated HTML hashes and playable HTTP 200 responses.
These development checks do not establish production readiness.
The endpoint supports `2026-07-28` and Streamable HTTP `2025-03-26`, `2025-06-18` and `2025-11-25`.
Each request is authenticated independently; no MCP session ID or session store is used. Older clients initialize
on the same HTTPS endpoint. Their POST responses can use bounded SSE, while GET/DELETE remain 405.
The old separate HTTP+SSE transport and stdio bridges are not supported. Record the actual negotiated version.

## Hosted provider checks

Use a development HTTPS endpoint reachable by the provider. Connect OAuth, read documentation/account data,
list games, publish a tiny HTML game, update it, then verify near-limit signed upload if the client can send files.
Capture the actual protocol version and results; transport support alone is insufficient.
ChatGPT and Claude custom connectors passed browser OAuth, reads and inline create/update in development.
Lovable, Replit and Grok hosted previously passed DCR/browser OAuth but failed the former strict protocol gate.
All three now pass browser OAuth, tool discovery, account/docs/list and inline create/update against the expanded
stateless transport in development. Lovable used `2025-11-25`. Their final plain HTML games loaded in the web
player and passed a Play→Played interaction. Native PlayDrop app playback is unverified; production acceptance
remains pending.
Grok Bot is a separate, paid-plan-gated surface on the tested account; hosted chat results cannot establish Bot support.
For Lovable, add a custom MCP server in Connectors. For Replit, add a personal MCP server in Integrations.
For Grok hosted chat, add a custom connector in Plugins, then select it in the conversation. Use the same HTTPS
endpoint and PlayDrop OAuth; no provider-specific plugin or compatibility service is required for these URL flows.
Muse documents private custom connectors, but does not document whether that route supports arbitrary MCP URLs.
Its public submission form accepts an existing hosted MCP with OAuth PKCE; request testing details during onboarding.

## Submission materials

For reviewed stores/directories, prepare the public repository URL, endpoint, documentation, support contact,
privacy/terms URLs, icon, sample prompts, account requirements, limits and reproducible provider test evidence.
Confirm provider-specific OAuth callbacks/client registration separately from directory approval.
Do not mark a connector released until both its production acceptance check and provider review have completed.

## Sources

- [Agent Plugins specification](https://agent-plugins.org/specification)
- [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [Claude Code plugins](https://code.claude.com/docs/en/plugins)
- [Antigravity plugins](https://www.antigravity.google/docs/plugins)
- [Antigravity MCP](https://www.antigravity.google/docs/mcp/)
- [Grok Build plugins](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/09-plugins.md)
- [Lovable custom MCP](https://docs.lovable.dev/integrations/custom-mcp)
- [Replit MCP](https://docs.replit.com/build/connect-via-mcp)
- [Gemini custom MCP eligibility](https://support.google.com/gemini/answer/17209137)
- [Muse submission](https://muse.ai/platform)
- [Muse custom connectors](https://www.meta.com/en-gb/help/artificial-intelligence/1687253048996149/)
