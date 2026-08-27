# PlayDrop game servers

Use this capability for every new multiplayer or server-authoritative game. It is the only supported way for a game to run custom server-side code. Prefer a client-only game only when it needs no realtime multiplayer, trusted server rules, shared authoritative state, or server-owned persistent data.

PlayDrop Cloud game servers use the standard Colyseus 0.17 API and the standard MongoDB Node.js driver. PlayDrop adds hosting, connection material, verified player identity, and limits. It does not wrap rooms, state, messages, or MongoDB.

The older `sdk.rooms` and `sdk.me.joinRoom()` APIs use PlayDrop's legacy realtime service. They remain available only for existing games and are deprecated. New games must declare a game server and connect through `sdk.multiplayer.getConnection()` as shown below.

## Frozen project contract

Install and keep the exact package versions required by `playdrop project check`. Declare the entry and room names in `catalogue.json`:

```json
{
  "server": {
    "entry": "server/index.ts",
    "rooms": ["game"]
  }
}
```

The server entry exports ordinary room definitions:

```ts
import { defineRoom } from "colyseus";
import { GameRoom } from "./GameRoom.js";

export const rooms = {
  game: defineRoom(GameRoom),
};
```

PlayDrop installs authentication on every exported room before it starts. Creator code reads the verified identity from standard Colyseus `client.auth`:

```ts
import { Room } from "colyseus";
import type { PlayDropPlayer } from "@playdrop/server";

export class GameRoom extends Room {
  onJoin(client: { auth: PlayDropPlayer }): void {
    console.log(client.auth.userId, client.auth.appRole, client.auth.isTestPlayer);
  }
}
```

Treat `client.auth` as trusted platform identity. `appRole` is `OWNER` only when the player owns the app. Keep match teams, moderators, and game roles inside the game. Do not define `onAuth`; the host owns that security boundary.

## AI-generated assets

Server code can create private AI assets through the narrow PlayDrop server SDK. The app creator always pays. The creator owns the result unless the call assigns it to a verified player:

```ts
import { playdrop } from "@playdrop/server";

const creatorOwned = await playdrop.ai.image.createTask({
  input: "A friendly forest merchant on a transparent background",
  imageSize: "4K",
});

const playerOwned = await playdrop.ai.image.createTask(
  {
    input: "A personalized bronze shield on a transparent background",
    imageSize: "1K",
  },
  { owner: client.auth },
);

const current = await playdrop.ai.tasks.get(playerOwned.id);
```

Only pass a `PlayDropPlayer` received through `client.auth`. Passing a local test-player identity keeps the generated asset creator-owned and labels the task as test mode. The server package does not expose arbitrary HTTP access or asset-pack creation.

## Social messages

The same verified player carries an app, version, deployment, and session-scoped social grant. Pass that exact `client.auth` object to the narrow server social API:

```ts
import { playdrop } from "@playdrop/server";

const playing = await playdrop.social.listGameFriends(client.auth);
await playdrop.social.sendMessage(client.auth, {
  recipientUserId: opponentId,
  type: "turn",
  title: "Your turn",
  payload: matchId,
  clientMessageId,
});
const pending = await playdrop.social.getMessages(client.auth, { limit: 20 });
await playdrop.social.consumeMessage(client.auth, pending.messages[0].messageId);
```

There is no server friend picker. The browser chooses a friend through PlayDrop's UI and the game server still validates game participation. Chat carries invitations and turn notices; MongoDB remains authoritative for match state. Notification failure must not roll back an already committed game action.

## Client connection

Load the pinned official client, request fresh connection material immediately before a new join, then use Colyseus directly:

```ts
const colyseus = await sdk.libs.colyseus.load();
const connection = await sdk.multiplayer.getConnection();
const client = new colyseus.Client(connection.endpoint);
client.auth.token = connection.token;
const room = await client.joinOrCreate("game");
```

Use normal Colyseus state, messages, reconnection, and matchmaking. Do not create a second game socket or send identity in game-defined messages.

## MongoDB

MongoDB is available only in server code. Use the real driver and the injected app-scoped URL:

```ts
import { MongoClient } from "mongodb";

const mongo = new MongoClient(process.env.PLAYDROP_MONGO_URL!);
await mongo.connect();
const matches = mongo.db().collection("matches");
```

The credential can read and write only the current game database. Published versions share the app database so updates retain data. Define indexes explicitly, keep documents under MongoDB's native 16 MiB limit, and close clients when the room process shuts down. Browsers never receive this URL.

Use `sdk.me.appData` for the existing client save behavior. Do not invent a client MongoDB bridge or `saveData` API.

## Development and validation

Run `playdrop project check`, then `playdrop project dev`. The CLI requires the exact native Redis and MongoDB services configured by the environment and fails clearly if they are absent. It never installs or starts them. PlayDrop Cloud managed workers provision those native services before tasks start and give each concurrent task its own scoped Redis and MongoDB credentials.

Validate with at least two PlayDrop test players through hosted `/dev`. Exercise join, leave, late join, reconnect, malformed authentication, cross-version authentication, and owner-versus-player behavior. For shared room invitations, put the game-defined room ID in `sdk.host.share({ payload })`; PlayDrop pins the immutable app version but does not authorize the payload for the game.

## Limits and unavailable surfaces

V1 supports at most two room types, eight players per room, a four-hour room lifetime, and a 2 MiB compiled bundle. Each active app version gets its own limited runtime, and one runtime can host many rooms for that version. Empty runtimes stop after 60 seconds. There is no fixed global app-version process cap. `playdrop project check` is authoritative for frozen package versions and allowed imports.

Game code cannot replace PlayDrop's transport, driver, or presence; import Redis; use subprocesses, workers, native addons, or arbitrary dependencies; expose an HTTP server; access persistent local files; call arbitrary outbound services; or administer MongoDB. The allowlisted `playdrop.ai` and `playdrop.social` methods are the only outbound server APIs in v1. Fail explicitly when the desired game requires an unavailable capability.
