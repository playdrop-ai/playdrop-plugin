# Rapier

Use Rapier only when the game needs real physics beyond simple overlap checks.

- Load it from `sdk.libs.rapier.load()`. The loader initializes the pinned WASM runtime before it resolves, so create the world directly and do not call `init()` again.
- Keep physics deterministic enough for replay/restart.
- Make collisions visible and forgiving.
- Avoid adding physics complexity before the core loop is fun.
- If physics breaks the requested mechanic, simplify the collision shapes before adding more systems.
