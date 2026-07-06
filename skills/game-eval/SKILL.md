---
name: game-eval
description: "Judge frozen PlayDrop game versions inside an internal GAME_EVAL task and submit the strict eval result."
---

# Game Eval

Use this only inside a PlayDrop `GAME_EVAL` worker task. The server work order is authoritative: it names the mode, judge prompt version, targets, launch URLs, creator prompts, and output JSON contract.

## Boundaries

- Evaluate only the target app versions named in the task.
- Use only the staged public PlayDrop plugin, the task workspace, the launch URLs, and `./bin/playdrop`.
- Do not upload games, submit publish reviews, run `task done`, inspect platform source, or read credentials.
- If tooling, access, validation, or submission fails, run `./bin/playdrop task fail --message "<clear operational reason>"`.

## References

Read the staged references before scoring:

- `.playdrop/plugin/references/game-review-evidence-capture.md`
- `.playdrop/plugin/references/game-review-rating-scale.md`
- `.playdrop/plugin/references/game-review-score-caps.md`
- `.playdrop/plugin/references/dimensions.md`
- `.playdrop/plugin/references/quality-bars.md`

## Workflow

1. Read the task work order and identify every target id, creator prompt, launch URL, and primary surface hint.
2. Phase 1 PLAY: open each launch URL with `./bin/playdrop project capture remote`, play adaptively, and score request_fidelity, core_loop_fun, controls, polish, and stability from player experience only.
3. Write the Phase 1 notes immediately once evidence is sufficient. If play is inconclusive, record low scores with the observed reason instead of forcing progress.
4. Phase 2 AUDIT: inspect listing metadata, hero/icon/screenshots/video when provided by the work order or reachable from the game page, then score store_listing. Do not change Phase 1 scores after the audit.
5. Save the strict JSON result requested by the work order.
6. Submit with `./bin/playdrop task submit-eval --result-file <path>`.

For pairwise or n-way evals, judge each target independently before choosing a winner. Ties are valid when the work order tie band says the difference is not meaningful.

## Result JSON

`targets` must be an array. Do not write an object keyed by target id. `overall` must be a number from 1 to 10. Use this shape exactly:

```json
{
  "mode": "pairwise",
  "judgePromptVersion": "new-game-judge-v2.0.1",
  "summary": "One concise verdict sentence.",
  "winnerTargetId": null,
  "tie": true,
  "tieBand": 1.75,
  "targets": [
    {
      "targetId": "target-1",
      "overall": 2,
      "dimensions": {
        "request_fidelity": { "score": 2, "comment": "Short observed reason.", "caps": [], "subChecks": {} },
        "core_loop_fun": { "score": 2, "comment": "Short observed reason.", "caps": [], "subChecks": {} },
        "controls": { "score": 2, "comment": "Short observed reason.", "caps": [], "subChecks": {} },
        "polish": { "score": 2, "comment": "Short observed reason.", "caps": [], "subChecks": {} },
        "stability": { "score": 2, "comment": "Short observed reason.", "caps": [], "subChecks": {} },
        "store_listing": { "score": 2, "comment": "Short observed reason.", "caps": [], "subChecks": {} }
      },
      "comments": "Target-level notes and evidence summary.",
      "evidence": {}
    }
  ]
}
```
