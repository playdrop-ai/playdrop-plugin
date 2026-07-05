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

1. Open the launch URL with `./bin/playdrop project capture remote`.
2. Choose the primary scored surface from the target support: mobile portrait, mobile landscape, then desktop.
3. Capture core play, win or meaningful progression, and loss or failure. Use best progression for long games and say so.
4. Build the composite with `./bin/playdrop review compose-evidence`.
5. Write internal assessment and creator feedback in the public review format.
6. Generate the rating card with `./bin/playdrop review rating-card`.
7. Validate with `./bin/playdrop review validate-result`.
8. Submit with `./bin/playdrop task submit-review --state <STATE> --message-file <path> --creator-feedback-file <path> --evidence-dir <dir>`.

Use `./bin/playdrop task fail --message "<clear operational reason>"` only for operational failures that prevent a meaningful review.
