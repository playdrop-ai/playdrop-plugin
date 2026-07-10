# Game Review Evidence Capture

Evidence capture is mandatory. This workflow reviews gameplay quality, not whether a page launches.

## Primary review surface

Choose exactly one primary scored surface from the claimed version's `surfaceTargets`, in this priority order:

1. `MOBILE_PORTRAIT`
2. `MOBILE_LANDSCAPE`
3. `DESKTOP`

Use that surface for the scored review, screenshots, and score comments. Do not average across surfaces.

If `surfaceTargets` is missing or empty in the claimed payload, stop with `ERROR`; do not guess. If the chosen surface fails because the game falsely declares support for it, score the failure on that surface. You may do small smoke checks on other declared surfaces only to document metadata problems, not to rescue the score.

## Browser lifecycle

Drive the scored play session through Claude Code `--chrome`. Do not import Playwright or use another browser driver for review decisions. Do not use AppleScript, `osascript`, `cliclick`, CGEvent tools, JavaScript input injection, or coordinate scripts to force gameplay. Before scoring, the canary must know the exact expected host GPU renderer string recorded for this machine, record the actual WebGL renderer string in evidence, and require an exact match. The expected renderer string is supplied by the work order or worker environment for this machine; never infer it from local files and never match a shortened form, only the full recorded string exactly. If the expected value is missing, the actual renderer mismatches, SwiftShader appears, or ordinary Claude Code `--chrome` clicks, taps, and key presses cannot create the needed visible input effect, submit `instrument_error`.

Required cleanup order:

1. stop tracing or video if enabled
2. close every Claude `--chrome` tab opened for this task
3. close every visible Chrome artifact window opened with `open -na`
4. close any direct iframe, local probe, or blank troubleshooting tab opened for this task
5. verify no task-owned Chrome window remains

Leave pre-existing user tabs alone. AppleScript or `osascript` is allowed only for this final cleanup, never for gameplay or input. If cleanup itself fails, report the cleanup error in the run output. Do not leave a task-owned Chrome instance running.

## Saving screenshot files

Use Claude Code `--chrome` for gameplay decisions. For PNG files, open the same launch URL in a visible Chrome artifact window while the task is still `RUNNING`, then save evidence with the native recorder helper. Review tokens are task-state scoped; if you open the URL after cancellation or completion, a `404` is expected and is not evidence.

```bash
open -na "Google Chrome" --args --new-window "<launch-url>"
```

Then find the Chrome process and capture window:

```bash
pgrep -x "Google Chrome"
./bin/playdrop review list-windows --pid <chrome-pid>
```

Choose the window whose title matches the target game, then save each gameplay moment:

```bash
./bin/playdrop review screenshot \
  --pid <chrome-pid> \
  --window-id <window-id> \
  --out .tmp/game-review/<version-id>/core.png
```

Repeat for `win.png` and `loss.png`. The helper uses the approved native recorder, writes metadata beside the PNG, times out instead of hanging, and fails if the screenshot is blank. If you cannot get a nonblank screenshot of the visible Chrome artifact window while the task is running, submit `instrument_error`; do not score the game from memory and do not use full-screen `screencapture`, Playwright, `project check`, or listing capture output as a substitute.

## Gameplay screenshots

Capture screenshots at gameplay moments. Loading screens, title screens, splash screens, menus, and static launch proof do not count.

Required screenshots:

- `core`: a real core gameplay moment after the reviewer performs the primary action
- `win`: a win, completion, level clear, success, or meaningful progression moment
- `loss`: a fail, loss, timeout, mistake, blocked state, or evidence that the game has no reachable failure condition

Do not burn the review trying to force a true win in a non-deterministic, long-running, or deduction-heavy game. If a true win is not quickly reachable through normal player inputs, use the best meaningful progression or near-completion screenshot as `win.png`, then state that limitation in `Primary interaction evidence`, `Challenge evidence`, and `Score caps applied` when it affects quality.

If a required moment is impossible because the game has no working primary interaction, no success state, or no loss state, capture the clearest evidence of that absence and label it with the missing moment. The absence itself must affect scoring.

For the core screenshot, record the exact input sequence in the internal assessment's `Primary interaction evidence` line. The evidence must state what the reviewer did and what changed in gameplay. If a darts or throwing game only allows the reviewer to drag or place a dart at the final hit location, that is evidence that the throw verb is absent, even if the game shows hit, clear, or fail modals.

Also record `Challenge evidence`. This must state what made play interesting or what failed to do so. If the reviewer can complete the captured core, win, or progression moments without timing, planning, aim, risk, pressure, or meaningful decisions, that absence is evidence against gameplay quality.

Write screenshots under `.tmp/game-review/<version-id>/` using stable names:

- `.tmp/game-review/<version-id>/core.png`
- `.tmp/game-review/<version-id>/win.png`
- `.tmp/game-review/<version-id>/loss.png`

Build the composite:

```bash
playdrop review compose-evidence \
  --core .tmp/game-review/<version-id>/core.png \
  --win .tmp/game-review/<version-id>/win.png \
  --loss .tmp/game-review/<version-id>/loss.png \
  --out .tmp/game-review/<version-id>/composite.png
```

The composite is required evidence. Do not post it to Slack yourself. `playdrop task submit-review` sends it to the PlayDrop API, and the API uploads it to the review Slack thread.

## Rating card image

After writing and validating the internal review message, create a final ratings image:

```bash
playdrop review rating-card \
  --review-message-file <INTERNAL.txt> \
  --out .tmp/game-review/<version-id>/rating-card.png \
  --title "<game display name> v<version>"
```

The rating card uses the 10 criterion ratings, the `Outcome` line, and the `Punchline assessment` line from the internal review message.

The rating card is required evidence. Do not post it to Slack yourself. `playdrop task submit-review` sends it to the PlayDrop API, and the API uploads it after the gameplay evidence composite.
