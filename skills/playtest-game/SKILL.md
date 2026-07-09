---
name: playtest-game
description: "Self-playtest a PlayDrop game before upload or publish, including required evidence moments and lifecycle checks."
---

# Playtest Game

Use this before upload, publish, or task completion.

## Deterministic Check

Run the real hosted shell with installed headed Chrome:

```sh
./bin/playdrop project check . --screenshot assets/marketing/playdrop/screenshots/landscape/01-check.png
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
./bin/playdrop project check . --actions playtest-actions.json --screenshot assets/marketing/playdrop/screenshots/landscape/01-check.png
```

`project check` focuses the game frame before dispatching actions, validates the WebGL renderer, records console/page/request failures, and exits nonzero on failure. Fix failures before upload. Do not use an agent browser, `project capture remote`, Playwright CLI, or an alternate browser driver for builder playtest evidence.

Write `playtest-evidence.json` after the final successful check. This is validation evidence, not a design document. Include:

- `url`
- `surface`
- `captures`
- `actions`
- `statesObserved`
- `consoleErrors`
- `webglRenderer`
- `environment`
- `checkedAt`

Example:

```json
{
  "version": 1,
  "entries": [
    {
      "environment": "local",
      "url": "http://localhost:8080/creators/playdrop/apps/game/sky-orchard-glider/dev",
      "surface": "mobilePortrait",
      "captures": [
        "assets/marketing/playdrop/screenshots/portrait/01-check.png"
      ],
      "actions": ["project check", "click start", "press ArrowRight"],
      "statesObserved": ["hosted shell ready", "input dispatched", "core scene visible"],
      "consoleErrors": [],
      "webglRenderer": "ANGLE (Apple, ANGLE Metal Renderer: Apple M-series, Unspecified Version)",
      "checkedAt": "2026-07-05T00:00:00.000Z"
    }
  ]
}
```

The final self-playtest must happen after the last source-code change.

## Checklist

- First frame is not blank, title-only, menu-only, or offscale.
- Input works through focused game-frame actions.
- Core loop completes or progresses visibly.
- Restart or replay works.
- Preview state renders a meaningful live scene.
- Pause/resume does not advance play-critical state.
- Console logs contain no uncaught errors.
- HUD is small, safe-area aware, and does not steal game space.

Fix failures before upload. If a task cannot be fixed in scope, fail clearly.
