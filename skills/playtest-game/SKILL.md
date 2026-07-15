---
name: playtest-game
description: "Self-playtest a PlayDrop game before upload or publish, including required evidence moments and lifecycle checks."
---

# Playtest Game

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use this before uploading or publishing.

## Deterministic Check

Run the real hosted shell with installed headed Chrome:

```sh
playdrop project check . --screenshot evidence/01-check.png
```

For input-dependent games, add a small action file and rerun the check:

```json
[
  { "type": "click", "x": 640, "y": 360 },
  { "type": "press", "key": "ArrowRight" },
  { "type": "wait", "ms": 500 }
]
```

```sh
playdrop project check . --actions playtest-actions.json --screenshot evidence/02-check.png
```

`project check` focuses the game frame before dispatching actions, validates the WebGL renderer, records console/page/request failures, and exits nonzero on failure. Fix failures before upload. Do not use an agent browser, Playwright CLI, or any capture path other than `playdrop project check` for builder playtest evidence.

## Evidence

Write `playtest-evidence.json` after the final successful check. This is validation evidence, not a design document. Include per entry: `url`, `surface`, `captures`, `actions`, `statesObserved`, `consoleErrors`, `environment`, `checkedAt` (plus optional extras such as `webglRenderer`); and for a new game the top-level `proof` object:

- `proof.primaryInput`: the exact action, the visible response, and its capture path.
- `proof.win`: the action or sequence, the visible success state, and its capture path. For endless or story games this is the designed success moment: a reached milestone, completed chapter, or new-best overlay.
- `proof.loss`: the action or sequence, the visible failure or pressure state, and its capture path.

Each proof moment needs its own capture taken while checking the FINAL source code; a stale capture from before the last code change is not proof. A staged capture mode, debug hook, source-code path, or prose claim is not playtest proof. The upload validates the proof object's exact shape and its error text prints the full expected schema: when it rejects, fix exactly what it names rather than guessing (listing-related preflight errors are expected until store-listing is done).

The final self-playtest must happen after the last source-code change.

## Checklist

- First frame is a designed screen of the game (the board's title or gameplay screen, real art), never blank, loading leftovers, default chrome, or offscale; core gameplay is reachable within one input.
- Input works through focused game-frame actions.
- Primary input produces a concrete visible response captured after the input.
- Core loop completes or progresses visibly.
- A real player path reaches and captures the success state.
- A real player path reaches and captures the failure or pressure state.
- No loss occurs before meaningful input is possible, and no overlay blocks the first interaction.
- Restart or replay works.
- Preview state renders a meaningful live scene.
- Pause/resume does not advance play-critical state.
- Console logs contain no uncaught errors.
- HUD is small, safe-area aware, and does not steal game space.
- One gameplay screenshot is recognizably the board's gameplay screen (or the hero direction when the board is advisory).

Fix failures before upload. If a problem cannot be fixed in scope, say so clearly instead of shipping it.
