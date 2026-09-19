# Installing and submitting PlayDrop

These are packaging instructions with dated development checks below.
Packaging validation, MCP protocol acceptance and browser OAuth onboarding are separate checks.
Select one package per client; do not install the portable and native variants together.
For development, use the generated package's endpoint instead of production in every provider form.
As of September 19, 2026, the public 1.0 source is prepared for rollout; matching server deployment and production
acceptance remain pending. Repository publication does not enable a provider directory listing.

## Packages

| Client | Package or connection | Discovery/public listing |
| --- | --- | --- |
| ChatGPT / Codex | Portable root; Codex fallback `plugins/playdrop` | Optional public directory review |
| Claude | Custom connector using endpoint and OAuth | Optional connector directory review |
| Claude Code | `variants/claude/playdrop` | Repo marketplace; public directory is separate |
| Gemini | Custom MCP is unavailable to the tested work account | Account eligibility gate |
| Antigravity | `variants/antigravity/playdrop` | Manual install; curated store is separate |
| Grok Bot | The tested account needs a paid plan | Do not equate with Grok Build |
| Grok Build | `variants/grok/playdrop` | Repo marketplace, no public listing required |
| Cursor | Tested CLI uses incompatible legacy MCP; skip | Cloud agent access also needs a paid plan |
| Lovable | Add a custom MCP chat connector with URL and OAuth | No listing required for private connection |
| Replit | Tested hosted client uses incompatible legacy MCP; skip | Recheck when its protocol changes |
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

Codex 0.153.4 needs the `mcp_2026_07_28` feature; Claude Code 2.1.270 needs `MCP_SDK_GENERATION=v2`.
Codex passed native browser OAuth, account/game reads, create/update and exact 5 MiB publishing in development.
Claude Code passed native plugin reads with programmatic fixture OAuth; its browser onboarding and writes remain
unchecked.
Grok Build 1.0.34's `mcp doctor` negotiated `2026-07-28` and discovered all seven tools.
Antigravity 1.2.7 also passed both read calls through its installed native plugin.
Its Google model login succeeded; PlayDrop authentication still used a programmatic fixture token.
Antigravity's PlayDrop browser onboarding/writes and Grok Build's onboarding/reads/writes remain unchecked.
These development checks do not establish production readiness.
Check the installed client version and negotiated protocol. If it cannot use `2026-07-28`, report it as blocked.
Do not add a compatibility proxy or silently negotiate an earlier protocol.

## Hosted provider checks

Use a development HTTPS endpoint reachable by the provider. Connect OAuth, read documentation/account data,
list games, publish a tiny HTML game, update it, then verify near-limit signed upload if the client can send files.
Capture the actual protocol version and results; transport support alone is insufficient.
ChatGPT and Claude custom connectors passed browser OAuth, reads and inline create/update in development.
Lovable offers a custom remote MCP form; an end-to-end connection has not yet been established.
Replit passed OAuth DCR, then sent legacy `initialize`; the strict endpoint correctly rejected it.
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
