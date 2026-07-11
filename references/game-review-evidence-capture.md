# Game Review Evidence Capture

Evidence capture is mandatory. This workflow judges gameplay quality, not whether a page launches. It applies to both `GAME_REVIEW` review tasks and `GAME_EVAL` judge tasks.

## One evidence surface

There is exactly one browser evidence surface: the controlled Claude Code `--chrome` gameplay tab. Every scored observation and every screenshot comes from that one tab. In an eval, each target has its own controlled tab.

A second evidence surface is structurally invalid and cannot be submitted. Never open a separate Chrome artifact window, never launch the game with `open -na`, and never capture with the native recorder helper. Those flows are deleted; the native recorder is listing capture only and is not review or judge evidence. Do not substitute full-screen `screencapture`, Playwright, `project capture remote`, `playdrop project check`, or listing capture output for a controlled-tab screenshot.

## Primary review surface

Choose exactly one primary scored surface from the claimed version's `surfaceTargets`, in this priority order:

1. `MOBILE_PORTRAIT`
2. `MOBILE_LANDSCAPE`
3. `DESKTOP`

Use that surface for the scored review, screenshots, and score comments. Do not average across surfaces.

If `surfaceTargets` is missing or empty in the claimed payload, stop with `ERROR`; do not guess. If the chosen surface fails because the game falsely declares support for it, score the failure on that surface. You may do small smoke checks on other declared surfaces only to document metadata problems, not to rescue the score.

## Browser lifecycle

Drive the scored play session through Claude Code `--chrome`. Do not import Playwright or use another browser driver for review decisions. Do not use AppleScript, `osascript`, `cliclick`, CGEvent tools, JavaScript input injection, or coordinate scripts to force gameplay.

Before the browser canary, if no Chrome browser is connected, run `open -a "Google Chrome"`, wait up to 30 seconds, and re-check once. If Chrome is still disconnected after that single re-check, clean up and exit with `task instrument-error --reason browser_control`. Never loop this wake.

The canary runs before scoring. It must know the exact expected host GPU renderer string recorded for this machine, record the actual WebGL renderer string in evidence, and require an exact match. The expected renderer string is supplied by the work order or worker environment for this machine; never infer it from local files and never match a shortened form, only the full recorded string exactly. Obtain the actual renderer ONLY with this exact probe in the game tab: `const gl=c.getContext('webgl2')||c.getContext('webgl'); const d=gl.getExtension('WEBGL_debug_renderer_info'); gl.getParameter(d.UNMASKED_RENDERER_WEBGL)`. `UNMASKED_RENDERER_INFO` does not exist; never invent another constant or probe, and a null, undefined, or error result is `instrument-error` with reason `renderer`, never evidence of browser masking. If the expected value is missing, the actual renderer mismatches, SwiftShader appears, or ordinary Claude Code `--chrome` clicks, taps, and key presses cannot create the needed visible input effect, exit with `instrument-error`.

Do not run recursive filesystem searches or scans outside the task workspace. Evidence lives in the task workspace and the browser.

## Screenshot ids and persistence

Capture each moment with the built-in Claude Chrome computer screenshot action. Every built-in screenshot returns a distinct `ss_...` id. The four captures for a review, or the four captures for one eval target, must come from the same controlled tab and must use four distinct screenshot ids. Reusing an id, or mixing ids from two tabs, invalidates the evidence.

Persist each capture as it is taken, by id. For a review:

```bash
./bin/playdrop task evidence --name core --screenshot-id ss_example --evidence-dir .tmp/evidence
```

Repeat with `--name first-frame`, `--name win`, and `--name loss`, each with its own distinct `ss_...` id.

For an eval, use one evidence directory per target and pass the target id as the evidence group:

```bash
./bin/playdrop task evidence --group target-1 --name core --screenshot-id ss_example --evidence-dir .tmp/evidence
```

Repeat all four names for every target.

The worker reads the screenshot bytes directly from the Claude stream-json output, then writes the named PNGs and `instrument-evidence.json` into the evidence directory. Submission verifies the screenshot id, tool-use id, tab id, source and file hashes, and decoded pixels against the immutable server transcript. Evidence that did not come from the controlled tab cannot pass that verification.

## Gameplay moments

Capture screenshots at gameplay moments. Loading screens, title screens, splash screens, menus, and static launch proof do not count as gameplay.

Required moments:

- `first-frame`: the first rendered frame of the controlled tab after the canary passes
- `core`: a real core gameplay moment after the reviewer performs the primary action
- `win`: a win, completion, level clear, success, or meaningful progression moment
- `loss`: a fail, loss, timeout, mistake, blocked state, or evidence that the game has no reachable failure condition

Do not burn the review trying to force a true win in a non-deterministic, long-running, or deduction-heavy game. If a true win is not quickly reachable through normal player inputs, use the best meaningful progression moment as `win`, then state that limitation in `Primary interaction evidence`, `Challenge evidence`, and `Score caps applied` when it affects quality.

If a required moment is impossible because the game has no working primary interaction, no success state, or no loss state, capture the clearest evidence of that absence and label it with the missing moment. The absence itself must affect scoring.

For the core capture, record the exact input sequence in the internal assessment's `Primary interaction evidence` line. The evidence must state what the reviewer did and what changed in gameplay. If a darts or throwing game only allows the reviewer to drag or place a dart at the final hit location, that is evidence that the throw verb is absent, even if the game shows hit, clear, or fail modals.

Also record `Challenge evidence`. This must state what made play interesting or what failed to do so. If the reviewer can complete the captured core, win, or progression moments without timing, planning, aim, risk, pressure, or meaningful decisions, that absence is evidence against gameplay quality.

## Review composite and rating card

These steps apply to `GAME_REVIEW` only. `task evidence` has already written the verified PNGs into the evidence directory; build the composite from those files.

```bash
playdrop review compose-evidence \
  --core .tmp/evidence/core.png \
  --win .tmp/evidence/win.png \
  --loss .tmp/evidence/loss.png \
  --out .tmp/evidence/composite.png
```

After writing and validating the internal review message, create the final ratings image:

```bash
playdrop review rating-card \
  --review-message-file <path> \
  --out .tmp/evidence/rating-card.png \
  --title "<game display name>"
```

The rating card uses the 10 criterion ratings, the `Outcome` line, and the `Punchline assessment` line from the internal review message.

The composite and the rating card are both required evidence. Do not post either to Slack yourself. `playdrop task submit-review` sends them to the PlayDrop API, and the API uploads the composite to the review Slack thread and the rating card after it.

## Cleanup before terminal submission

Browser cleanup happens before the terminal command, never after it. Close every tab and window the task opened, including every controlled Claude `--chrome` tab, and leave exactly one blank Chrome window. Leave pre-existing user tabs alone. AppleScript or `osascript` is allowed only for this final cleanup, never for gameplay or input. If cleanup itself fails, include the cleanup error in the final status.

Only then run the terminal command: `task submit-review` for a review, `task submit-eval` for an eval, or `task instrument-error`. That command is the final operation. Perform no browser operation after it.

## Instrument error

Instrument failure is a first-class exit and is never a game score. After browser cleanup, exit with:

```bash
./bin/playdrop task instrument-error --reason renderer
```

Reasons you may pass for failures you observe:

- `browser_control`: Chrome is not connected after the single wake re-check, or ordinary clicks, taps, and key presses cannot create the required visible input effect
- `renderer`: the expected renderer string is missing, the actual renderer mismatches, or SwiftShader appears
- `screenshot`: a required capture is blank, missing, or cannot be persisted with `task evidence`

`auth_state` is not passed by hand. Reviewer bootstrap failure or an auth or sign-in wall is terminated automatically by the shell as `instrument_error(auth_state)`; stop there. Never score such a run, never sign in, never inspect tokens, and never hunt for bypasses.

If the instrument is sound but the game itself remains unplayable or cannot show progress after serious adaptive play, that is not an instrument error. Record low scores with the observed game-side reason instead of forcing progress.
