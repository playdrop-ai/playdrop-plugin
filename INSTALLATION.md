# Install PlayDrop AI

Publish, update and share an HTML game from your AI agent. The public `playdrop` package contains one
`playdrop-ai` skill and a connection to `https://mcp.playdrop.ai/mcp`. Sign in to PlayDrop through OAuth.
The plugin does not install the PlayDrop CLI or the former collection of game-development skills.

The production endpoint and OAuth registration discovery are live. Provider directory approval and each provider's
production acceptance are separate checks; a public Git repository does not imply a reviewed directory listing.
Select one package per client. For local testing, use a generated development package and its endpoint throughout.

## Native agents: install the skill and MCP together

### Codex

Add the repository marketplace, then open the Plugins Directory and install PlayDrop from that marketplace:

```sh
codex plugin marketplace add playdrop-ai/playdrop-plugin
```

The repository's `.agents/plugins/marketplace.json` selects `plugins/playdrop`, the native Codex package.
For updates, run `codex plugin marketplace upgrade playdrop`, then refresh the installed plugin in the client.
See [OpenAI's marketplace guide](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli).

### Claude Code

Run inside Claude Code:

```text
/plugin marketplace add playdrop-ai/playdrop-plugin
/plugin install playdrop@playdrop
```

If Claude Code asks you to, run `/reload-plugins`. Then sign in: run `/mcp`, select `plugin:playdrop:playdrop`,
choose Authenticate and approve the connection in your browser. Until then, `/mcp` lists PlayDrop as
"Needs authentication". A PlayDrop plugin turned on at claude.ai also loads in Claude Code when you sign in with the
same Claude account.

From your game project, run `/playdrop:publish` (add `private` to test first) or ask Claude Code to publish the game.
It replies with the game's public link. The marketplace selects `variants/claude/playdrop`. See the
[Claude Code marketplace guide](https://code.claude.com/docs/en/plugin-marketplaces).

### Antigravity

Clone the public repository, then install its native variant:

```sh
git clone https://github.com/playdrop-ai/playdrop-plugin.git
agy plugin install ./playdrop-plugin/variants/antigravity/playdrop
```

This variant supplies Antigravity's `mcp_config.json` alongside the skill. Its CLI accepts a local package directory;
see [Antigravity plugins](https://www.antigravity.google/docs/plugins).

### Cursor

Cursor Agent CLI can load the portable root plugin (verified with Agent 2026.10.01) so the publishing skill and MCP
configuration are available together:

```sh
git clone https://github.com/playdrop-ai/playdrop-plugin.git
agent --plugin-dir ./playdrop-plugin
```

Review any trust prompt and complete PlayDrop OAuth. Loading the package is separate from successful game upload.
For a tools-only connection, use the manual configuration below.

In Cursor, open Customize → MCP and add PlayDrop, or merge this into `.cursor/mcp.json` at the project’s Git root
(or `~/.cursor/mcp.json` for a personal connection). Preserve existing server entries:

```json
{ "mcpServers": { "playdrop": { "url": "https://mcp.playdrop.ai/mcp" } } }
```

Enable the server and complete browser OAuth. In Cursor Agent CLI, run `agent mcp enable playdrop`, then
`agent mcp login playdrop`. Ask the agent to read your account and list games before attempting an upload.
A nested project configuration inside another Git repository may not be selected; use the actual Git root.
See [Cursor MCP setup](https://cursor.com/docs/mcp). Public marketplace approval is a separate check.
The native provider acceptance record below states what has actually been verified.

### Grok Build

Review the public package, then install its native variant:

```sh
grok plugin install 'playdrop-ai/playdrop-plugin#variants/grok/playdrop' --trust
```

`--trust` activates the package's skill and MCP connection. Start a new session or reload plugins afterward.
See [Grok Build's installation guide](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/09-plugins.md).
Grok Build, hosted Grok chat and Grok Bot are separate clients. Sign in to Grok Build itself with
`grok login --device-auth` if needed. `grok mcp doctor --json` includes plugin-provided MCP connections;
`grok mcp list` alone may omit those connections. Complete PlayDrop OAuth as well as the provider login.

## Hosted agents: connect the remote MCP

Use `https://mcp.playdrop.ai/mcp`, choose OAuth, and authorize your own PlayDrop account. Provider routes reviewed September 27, 2026; runtime evidence is dated below.
No client secret or access token belongs in this repository or an install link.

| Provider | Connection | Account or testing constraint |
| --- | --- | --- |
| ChatGPT | Plugins → Add → Create MCP App → MCP URL, OAuth → Create → Continue to PlayDrop | Custom MCP apps depend on account/workspace policy |
| Claude | Add [PlayDrop from the directory](https://claude.ai/directory/playdrop), or Customize → Connectors → Add custom connector | Free: one custom connector; organization policy applies |
| Lovable | Connectors → plus button → MCP server | All plans; workspace admins can disable custom MCP |
| Replit | Integrations → Add MCP server → Test & save | Complete OAuth; keep the security scanner enabled |
| Grok hosted chat | Plugins → Connectors → New Connector → Custom → Add Connector | Business/Enterprise admins provision connectors first |
| Gemini web / mobile | On the web: Settings → Connected Apps → Custom apps → Add → MCP URL → OAuth | US personal account, age 18+, English, Keep Activity on |
| Grok Bot | Personal custom MCP in Cursor dashboard → Grok Bot Your plugins → Authenticate | Cursor Pro or a linked eligible Grok subscription; Google sign-in alone is insufficient |
| Muse | Existing MCP onboarding with HTTPS and OAuth PKCE | Private runtime and review remain unverified |

[Add PlayDrop AI to Replit](https://replit.com/integrations?mcp=eyJkaXNwbGF5TmFtZSI6IlBsYXlEcm9wIEFJIiwiYmFzZVVybCI6Imh0dHBzOi8vbWNwLnBsYXlkcm9wLmFpL21jcCJ9)
pre-fills the public name and endpoint; sign-in and confirmation remain in Replit.

A URL connection supplies server tools. It does not by itself prove that the provider installed `playdrop-ai`.
OpenAI can import static MCP skills during submission or accept an uploaded bundle; imported skills are a snapshot,
not a live update channel. Other providers need their supported skill/package flow if you want the same instructions.
For Replit projects, copy the canonical `skills/playdrop-ai/SKILL.md` to `.agents/skills/playdrop-ai/SKILL.md`;
connect MCP separately. This skill installation path is documented by Replit but has not been provider-tested here.
Grok hosted chat also accepts a private skill through Plugins → Skills → New Skill → Write Manually. Use the
canonical name, description and Markdown body; this flow and subsequent `playdrop-ai` activation passed.

### Gemini on web, iOS and Android

Open [Gemini on the web](https://gemini.google.com) with an eligible personal Google account. In Settings, open
Connected Apps (some accounts show Personal Intelligence), then Custom apps → Add. Enter
`https://mcp.playdrop.ai/mcp`, continue and sign in to PlayDrop through OAuth. Ask Gemini which games you have
on PlayDrop to check the connection. Configure on the web first, then use Gemini on mobile with the same Google
account; there is no separate PlayDrop mobile connector package.

Google currently requires a personal US account, age 18+, English and Keep Activity enabled. Work/school Workspace
accounts are not eligible. Check these conditions if Custom apps is absent; a paid plan alone does not establish
eligibility. Review the activity setting yourself before changing it. Adding a custom app does not publish PlayDrop
in Google's app catalog. PlayDrop consumer web/mobile runtime validation remains pending; Antigravity acceptance
below is a separate client test. See [Google's setup guide](https://support.google.com/gemini/answer/17209137?hl=en)
and [iOS instructions](https://support.google.com/gemini/answer/17209137?co=GENIE.Platform%3DiOS&hl=en).

### First private game and update

Once connected, ask: “Read my PlayDrop account and the upload requirements. Make a small touch-friendly HTML game
and upload it privately. Give me its game ID and playtest link.” Open the returned game, then ask for one change
using that same game ID. Test the updated version before asking to publish it. Keep the game ID and link; retry an
interrupted upload using its existing request instead of creating a duplicate. Use the feedback tool to report a
problem with the client name, failed action and returned error.

### Grok Bot on mobile

Follow [Grok Bot’s mobile setup](https://docs.x.ai/grok-bot/mobile). On October 9, onboarding offered Cursor Pro or
Link Grok Account. Linking Grok required SuperGrok, SuperGrok Plus, SuperGrok Heavy or X Premium+; Google sign-in
alone did not satisfy this requirement. An existing linked SuperGrok Heavy account subsequently reached connector
setup on Cursor Free without a purchase or new trial. The full PlayDrop Bot create/update workflow remains unverified.

In a browser, open the [Cursor plugins dashboard](https://cursor.com/dashboard/plugins) with the same account as
Grok Bot. Choose **Personal**, then **Add → Custom MCP**. Set Name to **PlayDrop**, Type to **URL**, and Server URL
to `https://mcp.playdrop.ai/mcp`. Leave headers, Client ID and Client Secret blank, then select **Add MCP**.
Close and reopen **Connect Apps** in Grok Bot, then choose **Your plugins → PlayDrop → Authenticate** and complete
PlayDrop OAuth. This personal connection does not require a public marketplace listing; the directory search may
return no PlayDrop result. The dashboard’s “MCP Configured” status proves registration, not completed OAuth or uploads.
Hosted Grok chat acceptance and a Grok Build plugin installation do not validate Grok Bot.
Use [PlayDrop Web](https://www.playdrop.ai/create) if your account does not offer the required connection.

## Acceptance and compatibility

On September 19, 2026, production OAuth, reads and create/update passed in Codex, Claude Code, Antigravity,
ChatGPT, Claude, Lovable, Replit and Grok hosted chat. Codex also passed a signed 5 MiB upload and completion replay.
Those September 19 native plugin/skill checks used 1.0.5. On September 27, Antigravity 1.2.12
with native variant 1.0.8 passed OAuth and all eight tools, including private create/update, signed upload and cancellation.
SDK-free production games played in locally built iOS/Android apps, including taps and rotation. Those local builds do not establish released mobile-binary status. Historical macOS builds/focused tests and Windows
Core tests passed, without a Windows UI run.
Codex 0.153.4 used `mcp_2026_07_28`; Claude Code 2.1.270 used `MCP_SDK_GENERATION=v2` in the recorded modern tests.
Grok Build's development write run used native HTTP configuration; current plugin validation passed separately.
On October 9, Grok Build 1.0.50 provider login and native plugin loading passed. Fresh PlayDrop OAuth then
hit a consent CORS error; its fix is awaiting production deployment before create/update acceptance.
A prior record says Cursor’s publisher application was submitted, but the October 9 publisher portal shows a blank
application and no submission email was found in the work account. Submission status needs reconciliation; do not
describe it as currently in review. The earlier callback allowance is not a fresh production CLI acceptance.
Runtime acceptance and marketplace approval remain separate checks.
Individual directory approvals must be checked in the provider's listing.

The server supports MCP `2026-07-28` and Streamable HTTP `2025-03-26`, `2025-06-18`, `2025-11-25` without MCP
session IDs or a session store. Older POST responses may be bounded SSE; GET/DELETE return 405. There is no separate
HTTP+SSE endpoint or stdio bridge. Test account/docs/list, publish a small game, update it, and verify the returned URL.

## Sources and public listing

- [OpenAI connection/testing](https://developers.openai.com/plugins/deploy/connect-chatgpt)
  and [submission with skills](https://developers.openai.com/plugins/deploy/submission).
- [Claude custom connectors](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities)
  and [directory submission](https://claude.com/docs/connectors/building/submission).
- [Lovable custom MCP](https://docs.lovable.dev/integrations/custom-mcp).
- [Replit MCP](https://docs.replit.com/build/connect-via-mcp),
  [install links](https://docs.replit.com/features/mcp/overview#share-your-own-install-link)
  and [project skills](https://docs.replit.com/build/use-agent-skills).
- [Grok connectors](https://docs.x.ai/grok/connectors) and
  [Grok Bot team policy](https://docs.x.ai/grok-bot/teams-and-enterprises).
- [Gemini eligibility](https://support.google.com/gemini/answer/17209137).
- [Cursor plugin submission](https://cursor.com/docs/reference/plugins#submitting-a-plugin).
- [Muse onboarding](https://muse.ai/platform).

Public directories require their own review and publisher permissions. No provider submission is performed by
installing this repository. Use the current public guide at `https://www.playdrop.ai/docs/connectors`.
