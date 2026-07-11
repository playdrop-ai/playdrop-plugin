---
name: review-game
description: "Review a specific PlayDrop game version in a worker review task and submit the canonical public review result."
---

# Review Game

Use this only inside a PlayDrop `GAME_REVIEW` worker task. The task prompt provides the exact launch URL and target version.

## Boundaries

- Review only the launch URL and version named in the task.
- Use only the staged public PlayDrop plugin, the task workspace, and `./bin/playdrop`.
- Do not inspect platform source, admin sessions, API keys, Slack tokens, or internal repositories.
- Do not upload a game and do not run `task done`.
- Before the browser canary, if no Chrome browser is connected, run `open -a "Google Chrome"`, wait up to 30 seconds, and re-check once. If Chrome is still disconnected after that single re-check, clean up and exit with `./bin/playdrop task instrument-error --reason browser_control`. Never loop this wake.
- Do not run recursive filesystem searches or scans outside the task workspace. Evidence lives in the task workspace and the browser.

## Browser evidence surface

The review has exactly one browser evidence surface: the controlled Claude Code `--chrome` gameplay tab. Every scored observation and every screenshot comes from that one tab.

- Capture first-frame, core, win or progression, and loss or failure with the built-in Claude Chrome computer screenshot action.
- Never open an artifact window, never use `open -na`, never use `playdrop review list-windows`, and never use `playdrop review screenshot`. The native recorder is listing capture only and is not review evidence.
- Each built-in screenshot returns a distinct `ss_...` id. All four captures must come from the same controlled tab and must use four distinct screenshot ids.

The worker reads the screenshot bytes directly from the Claude stream-json output, writes the named PNGs and `instrument-evidence.json` into the evidence directory, and submission verifies the screenshot id, tool-use id, tab id, source and file hashes, and decoded pixels against the immutable server transcript. A second evidence surface is therefore structurally invalid and cannot be submitted.

## References

Read the staged game-review references before scoring:

- `.playdrop/plugin/references/game-review-criteria.md`
- `.playdrop/plugin/references/game-review-rating-scale.md`
- `.playdrop/plugin/references/game-review-score-caps.md`
- `.playdrop/plugin/references/game-review-gates.md`
- `.playdrop/plugin/references/game-review-outcomes.md`
- `.playdrop/plugin/references/game-review-feedback-format.md`
- `.playdrop/plugin/references/game-review-evidence-capture.md`
- `.playdrop/plugin/references/game-review-comparative-method.md`

## Workflow

1. Open the launch URL with Claude Code `--chrome` attached to the work Chrome profile. This tab is the controlled tab for the whole review.
2. Choose the primary scored surface from the declared surfaces, in this priority order when multiple are declared: mobile portrait, mobile landscape, then desktop. Standard viewports: MOBILE_PORTRAIT=390x844, MOBILE_LANDSCAPE=844x390, DESKTOP=1280x720.
3. Run the browser canary: know the exact expected host GPU renderer string recorded for this machine, record the actual WebGL renderer string in evidence, require an exact match to the expected string, verify one click with visible effect, verify one relevant key press with visible effect, and take a nonblank built-in screenshot of the controlled tab. The expected renderer string is supplied by the work order or worker environment for this machine; never infer it from local files and never match a shortened form, only the full recorded string exactly. Obtain the actual renderer ONLY with this exact probe in the game tab: `const gl=c.getContext('webgl2')||c.getContext('webgl'); const d=gl.getExtension('WEBGL_debug_renderer_info'); gl.getParameter(d.UNMASKED_RENDERER_WEBGL)`. `UNMASKED_RENDERER_INFO` does not exist; never invent another constant or probe, and a null, undefined, or error result is `instrument-error` with reason `renderer`, never evidence of browser masking. If the expected value is missing, the actual renderer mismatches, SwiftShader appears, or any other canary step fails, stop and exit with `instrument-error` instead of scoring.
4. Capture the first frame, core play, win or meaningful progression, and loss or failure through real adaptive play, all from the controlled tab. Use best progression for long games and say so. Persist each capture as it is taken:

   ```bash
   ./bin/playdrop task evidence --name core --screenshot-id ss_example --evidence-dir .tmp/evidence
   ```

   Repeat with `--name first-frame`, `--name win`, and `--name loss`, each with its own distinct `ss_...` id. If browser control, renderer, screenshot, or input evidence is inconclusive, exit with `instrument-error` instead of scoring. If the game itself remains unplayable or cannot show progress after serious adaptive play, record low scores with the observed game-side reason instead of forcing progress.
5. Build the composite from the verified PNGs with `./bin/playdrop review compose-evidence`.
6. Write internal assessment and creator feedback in the public review format.
7. Generate the rating card from the verified PNGs with `./bin/playdrop review rating-card`.
8. Validate with `./bin/playdrop review validate-result`.
9. Close every tab and window this task opened, including the controlled Claude `--chrome` tab, and leave exactly one blank Chrome window. Leave pre-existing user tabs alone. AppleScript or `osascript` is allowed only for this final cleanup, never for gameplay or input. If cleanup fails, include the cleanup error in the final status.
10. Submit with `./bin/playdrop task submit-review --state <STATE> --message-file <path> --creator-feedback-file <path> --evidence-dir <dir>`. This is the final operation. Perform no browser operation after it.

## Instrument failure

Instrument failure is a first-class exit and is never a game score. After browser cleanup, exit with:

```bash
./bin/playdrop task instrument-error --reason renderer
```

Use `renderer`, `browser_control`, or `screenshot` for failures you observe. Reviewer bootstrap failure or an auth or sign-in wall is terminated automatically by the shell as `instrument_error(auth_state)`; stop there. Never score such a run, never sign in, never inspect tokens, and never hunt for bypasses. Like submission, `instrument-error` is the final operation, and no browser operation follows it.

Do not use `project capture remote`, Playwright CLI, fixed action files, `playdrop project check`, AppleScript, `osascript`, `cliclick`, CGEvent tools, JavaScript input injection, or alternate browser drivers for review decisions. If Claude Code `--chrome` cannot create the required visible input effect with ordinary browser clicks, taps, and key presses, exit with `instrument-error` instead of switching tools. `playdrop project check` output is development evidence only; never cite it for gameplay or review conclusions.

Use `./bin/playdrop task fail --message "<clear operational reason>"` only for operational failures that prevent a meaningful review.
