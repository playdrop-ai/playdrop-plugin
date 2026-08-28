# PlayDrop SDK

Read the installed `playdrop-sdk-types` README and declarations for API signatures, examples, and payload types. Runtime JavaScript comes from the PlayDrop CDN; the types package does not bundle a second runtime. Keep the typed SDK value rather than casting it to `any`.

## Choose the relevant modules

| Module | Capability |
| --- | --- |
| `host`, `device`, `connection` | Hosted lifecycle, input surface, audio policy, sharing, and connection status. |
| `me`, `achievements`, `leaderboards` | Player identity, simple client saves, achievements, and scores. |
| `multiplayer`, `libs.colyseus` | Connect to a PlayDrop game server using the standard Colyseus client. |
| `social` | Host friend selection, friends playing this game, game messages, profiles, and Chat. |
| `assets`, `libs` | Declared game assets and platform-provided runtime libraries. |
| `ai`, `shop`, `ads` | Generation, purchases, and advertising when the game needs them. |
| `tweaks`, `creator` | Game configuration and optional creator-owned editing and playtest notes. |

New multiplayer or server-authoritative games use [game servers](game-servers.md) and server-owned persistence. Deprecated client room APIs are for existing games only. Social messages carry invitations and turn notices; they do not supply matchmaking, stranger discovery, or authoritative match state. Use PlayDrop's picker and Chat instead of building a second friend picker or inbox.

## Hosted game workflow

- Initialize early, but never prompt for login during initialization. Request account features only after an explicit player action. Saves, achievements, and score submissions are always callable: do not gate them on account login.
- Signal host readiness only after the designed first screen is rendered and any capture hooks are installed. Respect host pause and audio policy.
- Preview shows a representative live scene; Play accepts input. Studio can switch the existing frame between Editor and Playtest, so handle phase changes and signal readiness after remounting.
- Mount an optional Editor before reading creator capabilities. A staged version may have no creator APIs yet; read Tweaks, Notes, or assets when the creator uses those actions.
- Trigger sharing from a player click or tap. Treat incoming launch payloads as untrusted input and authorize protected room access on the server.
- Declared packs and assets must appear in the game through the SDK asset manifest. Surface required-asset failures clearly; do not hide them with substitute content.
