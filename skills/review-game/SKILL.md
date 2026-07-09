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
3. Run the browser canary: real hardware WebGL renderer, one click with visible effect, one relevant key press with visible effect, and screenshot capture. If it fails, stop and submit `instrument_error` instead of scoring.
4. Capture core play, win or meaningful progression, and loss or failure through real adaptive play. Use best progression for long games and say so.
5. Build the composite with `./bin/playdrop review compose-evidence`.
6. Write internal assessment and creator feedback in the public review format.
7. Generate the rating card with `./bin/playdrop review rating-card`.
8. Validate with `./bin/playdrop review validate-result`.
9. Submit with `./bin/playdrop task submit-review --state <STATE> --message-file <path> --creator-feedback-file <path> --evidence-dir <dir>`.

Do not use `project capture remote`, Playwright CLI, fixed action files, `playdrop project check`, or alternate browser drivers for review evidence. `playdrop project check` output is development evidence only; never cite it for gameplay or review conclusions.

Use `./bin/playdrop task fail --message "<clear operational reason>"` only for operational failures that prevent a meaningful review.
