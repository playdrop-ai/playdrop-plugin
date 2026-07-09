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

1. Open the launch URL with Claude Code `--chrome` attached to the work Chrome profile.
2. Choose the primary scored surface from the target support: mobile portrait, mobile landscape, then desktop.
3. Run the browser canary: know the exact expected host GPU renderer string recorded for this machine, record the actual WebGL renderer string in evidence, require an exact match to the expected string, verify one click with visible effect, verify one relevant key press with visible effect, and save a nonblank screenshot from the visible Chrome artifact window with `./bin/playdrop review screenshot`. The production mini expects `ANGLE Metal: Apple M4 Pro`; local runs use the exact renderer recorded for that machine. If the expected value is missing, the actual renderer mismatches, SwiftShader appears, or any other canary step fails, stop and submit `instrument_error` instead of scoring.
4. Capture core play, win or meaningful progression, and loss or failure through real adaptive play. For file evidence, open the same launch URL in a visible Chrome artifact window while the task is still `RUNNING`, then use `./bin/playdrop review list-windows` once to select the target game window and `./bin/playdrop review screenshot` for `core.png`, `win.png`, and `loss.png`. Use best progression for long games and say so.
5. Build the composite with `./bin/playdrop review compose-evidence`.
6. Write internal assessment and creator feedback in the public review format.
7. Generate the rating card with `./bin/playdrop review rating-card`.
8. Validate with `./bin/playdrop review validate-result`.
9. Submit with `./bin/playdrop task submit-review --state <STATE> --message-file <path> --creator-feedback-file <path> --evidence-dir <dir>`.
10. Close every Chrome tab/window you opened for the task, including Claude `--chrome` tabs, artifact windows opened with `open -na`, direct iframe windows, local probe tabs, and extra blank tabs. Leave pre-existing user tabs alone. AppleScript or `osascript` is allowed only for this final cleanup, never for gameplay or input. If cleanup fails, include the cleanup error in the final status.

Do not use `project capture remote`, Playwright CLI, fixed action files, `playdrop project check`, AppleScript, `osascript`, `cliclick`, CGEvent tools, JavaScript input injection, or alternate browser drivers for review decisions. If Claude Code `--chrome` cannot create the required visible input effect with ordinary browser clicks, taps, and key presses, submit `instrument_error` instead of switching tools. `playdrop project check` output is development evidence only; never cite it for gameplay or review conclusions.

Use `./bin/playdrop task fail --message "<clear operational reason>"` only for operational failures that prevent a meaningful review.
