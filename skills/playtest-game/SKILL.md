---
name: playtest-game
description: "Self-playtest a PlayDrop game before upload or publish, with optional early evidence and a deterministic final check."
---

# Playtest Game

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use this before uploading or publishing.

Use `../../references/greybox-report.md` when a new or risky interaction benefits from explicit early evidence. It is optional working memory, not an upload artifact.

## Deterministic Check

Every new game declares `primarySurface` and one complete `playtestTapes` entry per enabled surface inside its app entry in `catalogue.json`. Author the tapes with the schema and defaults in `../../references/catalogue-json.md`.

An early tape can reduce risk when the core interaction is uncertain. After the final runtime change, run one final tape for every affected surface:

```sh
playdrop project check . --tape <surface> --screenshot evidence/final-check.png
```

The smoke check opens two equal-duration clean runs from `sdk.host.ready()`: one without input and one with the complete tape. It passes only when every tape action can be delivered, the game completes the tape without a runtime failure, and the tape produces a visible result that differs from the no-input run. The one-line CLI result reports only those mechanical facts and explicitly does not claim gameplay success. That pass is necessary but not sufficient: inspect the tape image and reject it when it shows a menu, game-over screen, score-zero state, idle opening, or failed attempt instead of successful active play.

For an update, add one baseline run only when reproducing the reported behavior. Otherwise do not launch an equivalent bare check: the tape already includes its equal-duration idle control. Add another run only after a concrete fix or for a distinct risk.

If an action or the game runtime fails, the CLI identifies the action number and reports the underlying error. If the tape completes but does not demonstrate visible interactivity, the CLI reports that outcome and prints the idle and tape screenshot paths. Fix the game or tape and rerun the same command.

The agent-task upload repeats the same smoke check against the staged artifact. Do not use an agent browser, Playwright CLI, or another capture path as a substitute for `playdrop project check`.

Run the final self-playtest after the last runtime change and before final capture and upload.

## Checklist

- First frame is a designed screen per `../../references/quality-bars.md`; core gameplay is reachable within one input.
- Input works through focused game-frame actions, and the primary input produces a concrete visible response captured after the input.
- Core loop completes or progresses visibly, and every supported-surface tape passes with inspected evidence per the Deterministic Check above.
- When the game defines success or failure states, confirm both during normal self-play.
- No loss occurs before meaningful input is possible, and no overlay blocks the first interaction.
- Restart or replay works.
- Preview state renders a meaningful live scene.
- Pause/resume does not advance play-critical state.
- Console logs contain no uncaught errors.
- HUD is small, safe-area aware, and does not steal game space.
- One gameplay screenshot recognizably matches the approved visual direction when one exists.

Fix failures before upload. If a problem cannot be fixed in scope, say so clearly instead of shipping it.
