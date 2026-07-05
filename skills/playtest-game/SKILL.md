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

Use `./bin/playdrop project capture . --surface <surface> --dev-auth anonymous --timeout 20 --screenshot <path> --log <path>`.

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
