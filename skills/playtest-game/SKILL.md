---
name: playtest-game
description: "Self-playtest a PlayDrop game before upload or publish, including required evidence moments and lifecycle checks."
---

# Playtest Game

Use this before upload, publish, or task completion.

## Required Captures

Capture on the primary surface:

- `start`: first frame after SDK ready shows the real game at intended scale.
- `mid`: core mechanic exercised by real input.
- `win-or-progression`: win, wave clear, level clear, lap, solved step, or best meaningful progression.
- `loss`: failure, restart, timeout, missed objective, or documented endless-game equivalent.

Use `./bin/playdrop project capture . --surface <surface> --dev-auth anonymous --timeout 30 --log-level info --screenshot <path>`.

Write `playtest-evidence.json` after the captures. This is validation evidence, not a design document. Include:

- `url`
- `surface`
- `captures`
- `actions`
- `statesObserved`
- `consoleErrors`
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
        "assets/marketing/playdrop/screenshots/portrait/01-start.png",
        "assets/marketing/playdrop/screenshots/portrait/02-core.png",
        "assets/marketing/playdrop/screenshots/portrait/03-progression.png",
        "assets/marketing/playdrop/screenshots/portrait/04-loss.png"
      ],
      "actions": ["started play", "steered through rings", "missed a ring", "used restart"],
      "statesObserved": ["preview", "play", "progression", "loss", "restart"],
      "consoleErrors": [],
      "checkedAt": "2026-07-05T00:00:00.000Z"
    }
  ]
}
```

The final self-playtest must happen after the last source-code change.

## Checklist

- First frame is not blank, title-only, menu-only, or offscale.
- Input works on the primary surface.
- Core loop completes or progresses visibly.
- Restart or replay works.
- Preview state renders a meaningful live scene.
- Pause/resume does not advance play-critical state.
- Console logs contain no uncaught errors.
- HUD is small, safe-area aware, and does not steal game space.

Fix failures before upload. If a task cannot be fixed in scope, fail clearly.
