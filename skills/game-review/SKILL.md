---
name: game-review
description: "Use when a PlayDrop worker task asks an agent to review a specific game version and submit the canonical review result."
---

# Game Review

Use this only inside a PlayDrop `GAME_REVIEW` worker task. The task prompt provides the exact launch URL and target version.

## Boundaries

- Review only the launch URL and version named in the task.
- Use only the staged public PlayDrop plugin, the task workspace, and `./bin/playdrop`.
- Do not look for platform source, admin sessions, API keys, Slack tokens, or internal repositories.
- Do not post Slack messages. The PlayDrop server posts Slack after `task submit-review`.
- Do not upload a game and do not run `task done`.

## References

Read these staged references before scoring:

- `.playdrop/plugin/references/game-review-criteria.md`
- `.playdrop/plugin/references/game-review-rating-scale.md`
- `.playdrop/plugin/references/game-review-score-caps.md`
- `.playdrop/plugin/references/game-review-gates.md`
- `.playdrop/plugin/references/game-review-outcomes.md`
- `.playdrop/plugin/references/game-review-feedback-format.md`
- `.playdrop/plugin/references/game-review-evidence-capture.md`
- `.playdrop/plugin/references/game-review-comparative-method.md`

## Workflow

1. Open the task launch URL with `./bin/playdrop project capture remote`.
2. Choose one primary scored surface from the target surface support: `MOBILE_PORTRAIT`, then `MOBILE_LANDSCAPE`, then `DESKTOP`.
3. Capture evidence screenshots for core play, win or meaningful progression, and loss or failure. Do not spend the run forcing a true win in non-deterministic or long-running games; use the best progression evidence as `win.png` and document the limitation.
4. Build the composite with `./bin/playdrop review compose-evidence`.
5. Write the internal assessment and creator feedback using the exact public review format.
6. Generate the rating card with `./bin/playdrop review rating-card`.
7. Validate locally with `./bin/playdrop review validate-result`.
8. Submit with:

```bash
./bin/playdrop task submit-review \
  --state <FAILED|LOW_QUALITY|PASSED|GOOD|EXCELLENT> \
  --message-file <internal-assessment.txt> \
  --creator-feedback-file <creator-feedback.txt> \
  --evidence-dir <evidence-dir>
```

Use `./bin/playdrop task fail --message "<clear operational reason>"` only for tooling, access, capture, validation, or infrastructure failures that prevent a meaningful review.

## Required Output Files

The evidence directory must contain:

- `core.png`
- `win.png` for true success, near-completion, or best meaningful progression
- `loss.png`
- `composite.png`
- `rating-card.png`

The internal assessment must include the outcome, gate, primary reviewed surface, primary verb, interaction evidence, challenge evidence, comparable benchmark, punchline, score caps applied, and all 10 criteria ratings.

The creator feedback must be private creator-facing text and must include `Reviewed surface: <SURFACE>`.
