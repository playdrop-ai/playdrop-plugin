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

Every new game declares top-level `primarySurface` and one complete `playtestTapes` entry per enabled surface in `catalogue.json`. Run the command once for every enabled surface before upload:

```sh
playdrop project check . --tape <surface> --screenshot evidence/02-check.png
```

Each tape declares `primaryVerb` (`tap`, `swipe`, `drag`, or `key`) and `startOnlyEventCount`. Show the same primary verb in the player-facing controls instruction. Post-start tape events must use only that verb family. Give every game an explicit startup action; its first event uses `atMs: 0`, relative to `sdk.host.ready()`. The check opens three equal-duration clean runs from that signal: zero input, only the startup prefix, then the complete timed tape. Inspect all three captures. Every tape passes only when start-only visibly leaves the title and the full run meaningfully beats both controls by surviving longer, scoring above zero and above both controls, making visible progress beyond both controls, or reaching a state neither control reaches. If it does not, fix the game or tape and rerun it.

`project check` waits for `sdk.host.ready()`, focuses the game frame before dispatching tape input, validates the WebGL renderer, records console/page/request failures, and exits nonzero on delivery or runtime failure. On agent tasks, the upload path repeats the causal runs against the staged hosted artifact, adds the first-action trivial-completion probe, and records fresh machine evidence on the upload session. It refuses failure even when `playtest-evidence.json` claims success. Fix failures before upload. Do not use an agent browser, Playwright CLI, or any capture path other than `playdrop project check` for builder playtest evidence.

## Evidence

Write `playtest-evidence.json` after the final successful check. This is validation evidence, not a design document. Include per entry: `url`, `surface`, `captures`, `actions`, `statesObserved`, `consoleErrors`, `environment`, `checkedAt` (plus optional extras such as `webglRenderer`); and for a new game the top-level `proof` and `causalChecks` objects.

- `proof.primaryInput`: the exact action, the visible response, and its capture path.
- `proof.win`: the action or sequence, the visible success state, and its capture path. For endless or story games this is the designed success moment: a reached milestone, completed chapter, or new-best overlay.
- `proof.loss`: the action or sequence, the visible failure or pressure state, and its capture path.

Each proof moment needs its own capture taken while checking the FINAL source code; a stale capture from before the last code change is not proof. A staged capture mode, debug hook, source-code path, or prose claim is not playtest proof. The upload validates the proof object's exact shape and its error text prints the full expected schema: when it rejects, fix exactly what it names rather than guessing (listing-related preflight errors are expected until store-listing is done).

Use this exact `causalChecks` shape as an honest creator report. It never authorizes or blocks upload: agent-task uploads always run the machine causal gate against the staged build. For non-3D games set `readability3D.applicable` to false and describe why the fields do not apply. When there is no visible replay control set `replay.applicable` to false and record the tested lifecycle path.

```json
{
  "causalChecks": {
    "matchedRuns": [{
      "surface": "MOBILE_PORTRAIT",
      "zeroInputOutcome": "Visible zero-input outcome.",
      "startOnlyOutcome": "Visible startup-only outcome.",
      "fullTapeOutcome": "Visible full-tape outcome.",
      "criterion": "The measurable difference produced by gameplay input.",
      "passed": true
    }],
    "counterfactual": {
      "normalInput": "Ordinary primary input.",
      "perturbedInput": "Opposite, perturbed, or invalid input.",
      "normalOutcome": "Visible normal outcome.",
      "perturbedOutcome": "Visible perturbed outcome.",
      "passed": true
    },
    "replay": { "applicable": true, "action": "Tap replay at its center.", "outcome": "A second playable run began.", "passed": true },
    "challenge": { "claim": "The promised loop.", "action": "Perform the first trivial valid action.", "outcome": "The sustained loop did not automatically complete.", "passed": true },
    "readability3D": { "applicable": false, "controlledEntity": "Not 3D.", "objectiveOrHazard": "Not 3D.", "primaryActionEffect": "Not 3D.", "passed": true }
  }
}
```

The final self-playtest must happen after the last source-code change.

## Checklist

- First frame is a designed screen per the direction contract, never blank, loading leftovers, default chrome, or offscale; core gameplay is reachable within one input.
- Input works through focused game-frame actions.
- Primary input produces a concrete visible response captured after the input.
- Every supported-surface full tape visibly beats both its matched zero-input and start-only controls; the primary-surface triplet is retained as acceptance proof.
- The game-appropriate primary-verb counterfactual produces a measurable outcome difference.
- A visible replay control begins a second playable run when one exists.
- The first trivial action does not automatically complete a claimed sustained loop.
- In 3D play, the controlled entity, objective or hazard, and primary-action effect remain readable on the primary surface.
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
