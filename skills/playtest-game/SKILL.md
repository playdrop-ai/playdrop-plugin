---
name: playtest-game
description: "Self-playtest a PlayDrop game before upload or publish, including required evidence moments and lifecycle checks."
---

# Playtest Game

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use this before uploading or publishing.

Follow `../../references/greybox-report.md`. The prototype checks happen before assets and listing; the final checks happen before the final deterministic check below. Both report sections must pass.

## Deterministic Check

Run the real hosted shell with installed headed Chrome:

```sh
playdrop project check . --screenshot evidence/01-check.png
```

Every new game declares top-level `primarySurface` and one complete `playtestTapes` entry per enabled surface in `catalogue.json`.

Create a short tape that demonstrates the game’s core interaction:

- Target about 10 seconds.
- Use 3 to 6 representative gameplay actions, plus a start action when the game needs one.
- Focus the tape on the declared `primaryVerb` (`tap`, `swipe`, `drag`, or `key`).
- Show one short core gameplay loop with a visible player-driven response or progress.
- When the game has a title screen, put its start action first and set `startOnlyEventCount` to the number of startup events so later reviewers can distinguish startup from gameplay.

These are strong defaults, not arbitrary validation limits. A game may use a somewhat different duration or action count when its core interaction genuinely requires it.

Run the command as soon as the core loop works, then run it again after the final source-code change. Run it once for every enabled surface:

```sh
playdrop project check . --tape <surface> --screenshot evidence/02-check.png
```

The smoke check opens two equal-duration clean runs from `sdk.host.ready()`: one without input and one with the complete tape. It passes only when every tape action can be delivered, the game completes the tape without a runtime failure, and the tape produces a visible result that differs from the no-input run.

If an action or the game runtime fails, the CLI identifies the action number and reports the underlying error. If the tape completes but does not demonstrate visible interactivity, the CLI reports that outcome and prints the idle and tape screenshot paths. Fix the game or tape and rerun the same command. Passing this check is required for the creation task to succeed and gives you a chance to iterate before upload.

The agent-task upload repeats the same smoke check against the staged artifact. Do not use an agent browser, Playwright CLI, or another capture path as a substitute for `playdrop project check`.

## Evidence

Write `playtest-evidence.json` after the final successful check. This is validation evidence, not a design document. Include per entry: `url`, `surface`, `captures`, `actions`, `statesObserved`, `consoleErrors`, `environment`, `checkedAt` (plus optional extras such as `webglRenderer`); and for a new game the top-level `proof` object.

- `proof.primaryInput`: the exact action, the visible response, and its capture path.
- `proof.win`: the action or sequence, the visible success state, and its capture path. For endless or story games this is the designed success moment: a reached milestone, completed chapter, or new-best overlay.
- `proof.loss`: the action or sequence, the visible failure or pressure state, and its capture path.

Each proof moment needs its own capture taken while checking the FINAL source code; a stale capture from before the last code change is not proof. A staged capture mode, debug hook, source-code path, or prose claim is not playtest proof. The upload validates the proof object's exact shape and its error text prints the full expected schema: when it rejects, fix exactly what it names rather than guessing (listing-related preflight errors are expected until store-listing is done).

The final self-playtest must happen after the last source-code change.

## Checklist

- First frame is a designed screen per the direction contract, never blank, loading leftovers, default chrome, or offscale; core gameplay is reachable within one input.
- Input works through focused game-frame actions.
- Primary input produces a concrete visible response captured after the input.
- Every supported-surface tape completes without a runtime failure and produces a visible result that differs from its equal-duration no-input run.
- Core loop completes or progresses visibly.
- A real player path reaches and captures the success state.
- A real player path reaches and captures the failure or pressure state.
- No loss occurs before meaningful input is possible, and no overlay blocks the first interaction.
- Restart or replay works.
- Preview state renders a meaningful live scene.
- Pause/resume does not advance play-critical state.
- Console logs contain no uncaught errors.
- HUD is small, safe-area aware, and does not steal game space.
- One gameplay screenshot recognizably matches the direction contract (`../../references/art-direction-board.md` step 3).

Fix failures before upload. If a problem cannot be fixed in scope, say so clearly instead of shipping it.
