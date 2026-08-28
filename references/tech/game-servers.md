# PlayDrop game servers

Use this capability for every new multiplayer or server-authoritative game. It is the only supported way for a game to run custom server-side code. Prefer a client-only game only when it needs no realtime multiplayer, trusted server rules, shared authoritative state, or server-owned persistent data.

PlayDrop Cloud game servers use standard Colyseus for rooms, state, messages, reconnection, and matchmaking, and the standard MongoDB Node.js driver for persistence. PlayDrop adds hosting, connection material, verified player identity, and limits.

The older client room APIs use PlayDrop's deprecated realtime service and remain available only for existing games. New multiplayer games declare a game server and use the client SDK's `multiplayer` and `libs.colyseus` modules.

## Platform-managed SDK and project contract

Create `package.json` beside `catalogue.json`. Declare the server entry in `server.entry` and its exported room names in `server.rooms` on the app entry. See [the catalogue contract](../catalogue-json.md).

Run `playdrop project build` before invoking your own TypeScript build. The CLI reads the target environment's active game-server SDK version, downloads its verified archive from the same CDN as the client SDK, and installs the matching server dependencies automatically. `project check`, `project dev`, and upload preflight use the same selection. The CLI updates `package.json`, `package-lock.json`, and `vendor/playdrop/playdrop-server-<version>.tgz`; keep these files in the project. Do not try to install `@playdrop/server` from the npm registry or choose its version yourself.

Production provides the SDK in the hosted game-server runtime. A running process keeps its selected SDK until it stops; a new CLI command selects the currently deployed version. Missing SDK artifacts or unavailable runtime metadata are platform errors: report them and stop instead of replacing the server with Chat or client saves.

Read the installed `@playdrop/server` README for runtime and TypeScript setup, and its declarations for verified player types, server social APIs, and examples. Read the installed `playdrop-sdk-types` README and declarations for client APIs. These packages own the API reference; this skill describes capability selection and the creator workflow. Use the installed Colyseus and MongoDB packages for their standard APIs.

## Capabilities and boundaries

- **Identity:** PlayDrop authenticates every exported room. Use its verified player identity; keep match teams and game roles in the game. Do not replace platform authentication or accept player identity from game messages.
- **Persistence:** Server code connects to the app database using the injected `PLAYDROP_MONGO_URL`. Published versions share that database so updates retain data. Browsers never receive database credentials. Client saves do not provide shared authoritative state.
- **Persistent matches:** A `joinOrCreate` filter such as `matchId` is not a unique-room guarantee: it can create another live room when the existing one is full or locked. Keep reconnecting players in the same live match. Enforce game seats by verified player identity, and account for overlapping connections during refresh when setting `maxClients` and reconnection reservations. Verify both players can refresh and then rematch on the same shared board, not just reload the last saved result.
- **Social:** The client SDK provides PlayDrop's friend picker and Chat UI; the server SDK can send and consume game messages for verified players. Social is not stranger discovery or matchmaking. Chat carries invitations and turn notices, while the server and MongoDB own match state. A notification failure must not roll back a committed move.
- **AI assets:** The server SDK can create private AI assets. The app creator pays and owns the result unless ownership is assigned to a verified player. Test-player generation stays creator-owned and uses test mode. This capability does not provide arbitrary HTTP access or asset-pack creation.

## Development and validation

Run `playdrop project build`, `playdrop project check`, then `playdrop project dev`. SDK code and types are installed automatically; native Redis and MongoDB services are separate prerequisites. The CLI requires the exact native services configured by the environment and fails clearly if they are absent. It never installs or starts those services. PlayDrop Cloud managed workers provision them before tasks start and give each concurrent task its own scoped Redis and MongoDB credentials.

Follow the [multiplayer playtest procedure](../../skills/playtest-game/SKILL.md#multiplayer) to connect two distinct test players to one dev server. Verify shared state, reconnect, and durable data through a server restart. Check that invalid identities and wrong-version connections are rejected. Invitations and share payloads remain untrusted game input; the server authorizes room access.

## Limits and unavailable surfaces

V1 supports at most two room types, eight players per room, a four-hour room lifetime, and a 2 MiB compiled bundle. Each active app version gets its own limited runtime, and one runtime can host many rooms for that version. Empty runtimes stop after 60 seconds. There is no fixed global app-version process cap. `playdrop project check` is authoritative for frozen package versions and allowed imports.

Game code cannot replace PlayDrop's transport, driver, or presence; import Redis; use subprocesses, workers, native addons, or arbitrary dependencies; expose an HTTP server; access persistent local files; call arbitrary outbound services; or administer MongoDB. The allowlisted `playdrop.ai` and `playdrop.social` methods are the only outbound server APIs in v1. Fail explicitly when the desired game requires an unavailable capability.
