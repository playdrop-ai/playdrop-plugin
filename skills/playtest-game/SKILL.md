---
name: playtest-game
description: "Self-playtest a PlayDrop game before upload or publish, with optional early evidence and a deterministic final check."
---

# Playtest Game

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use this before uploading or publishing.

Use `../../references/greybox-report.md` when a new or risky interaction benefits from explicit early evidence. It is optional working memory, not an upload artifact.

## Deterministic Check

Every new game declares `primarySurface` and one complete `playtestTapes` entry per enabled surface inside its app entry in `catalogue.json`.

Create a short tape that demonstrates the game’s core interaction:

- Target about 10 seconds.
- Use 3 to 6 representative gameplay actions, plus a start action when the game needs one.
- Focus the tape on the declared `primaryVerb` (`tap`, `swipe`, `drag`, or `key`).
- Show one short core gameplay loop with a visible player-driven response or progress.
- When the game has a title screen, put its start action first and set `startOnlyEventCount` to the number of startup events so later reviewers can distinguish startup from gameplay.

These are strong defaults, not arbitrary validation limits. A game may use a somewhat different duration or action count when its core interaction genuinely requires it.

An early tape can reduce risk when the core interaction is uncertain. After the final runtime change, run one final tape for every affected surface:

```sh
playdrop project check . --tape <surface> --screenshot evidence/final-check.png
```

The smoke check opens two equal-duration clean runs from `sdk.host.ready()`: one without input and one with the complete tape. It passes only when every tape action can be delivered, the game completes the tape without a runtime failure, and the tape produces a visible result that differs from the no-input run. That mechanical pass is necessary but not sufficient: inspect the tape image and reject it when it shows a menu, game-over screen, score-zero state, idle opening, or failed attempt instead of successful active play.

For an update, add one baseline run only when reproducing the reported behavior. Otherwise do not launch an equivalent bare check: the tape already includes its equal-duration idle control. Add another run only after a concrete fix or for a distinct risk.

If an action or the game runtime fails, the CLI identifies the action number and reports the underlying error. If the tape completes but does not demonstrate visible interactivity, the CLI reports that outcome and prints the idle and tape screenshot paths. Fix the game or tape and rerun the same command.

The agent-task upload repeats the same smoke check against the staged artifact. Do not use an agent browser, Playwright CLI, or another capture path as a substitute for `playdrop project check`.

The final self-playtest must happen after the last runtime change and before capture-independent task preflight.

## Checklist

- First frame is a designed screen per the direction contract, never blank, loading leftovers, default chrome, or offscale; core gameplay is reachable within one input.
- Input works through focused game-frame actions.
- Primary input produces a concrete visible response captured after the input.
- Every supported-surface tape completes without a runtime failure and produces a visible result that differs from its equal-duration no-input run.
- Core loop completes or progresses visibly.
- The retained gameplay evidence shows a satisfying, high-pressure, or high-progress moment with meaningful score or progress, never a menu, game-over screen, score-zero state, or failed attempt.
- When the game defines success or failure states, confirm both during normal self-play.
- No loss occurs before meaningful input is possible, and no overlay blocks the first interaction.
- Restart or replay works.
- Preview state renders a meaningful live scene.
- Pause/resume does not advance play-critical state.
- Console logs contain no uncaught errors.
- HUD is small, safe-area aware, and does not steal game space.
- One gameplay screenshot recognizably matches the approved visual direction when one exists.

Fix failures before upload. If a problem cannot be fixed in scope, say so clearly instead of shipping it.
