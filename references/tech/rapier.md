# Rapier

Use Rapier only when the game needs real physics beyond simple overlap checks.

- Load it from `sdk.libs.rapier.load()`.
- Keep physics deterministic enough for replay/restart.
- Make collisions visible and forgiving.
- Avoid adding physics complexity before the core loop is fun.
- If physics breaks the requested mechanic, simplify the collision shapes before adding more systems.
