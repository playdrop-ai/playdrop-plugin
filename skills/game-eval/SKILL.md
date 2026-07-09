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
2. Phase 1 PLAY: open each launch URL with Claude Code `--chrome` attached to the work Chrome profile, play adaptively, and score request_fidelity, core_loop_fun, controls, polish, and stability from player experience only.
3. Run the browser canary before scoring: real hardware WebGL renderer, one click with visible effect, one relevant key press with visible effect, and screenshot capture. If it fails, write `instrument_error` instead of scoring.
4. Write the Phase 1 notes immediately once evidence is sufficient. If browser control, renderer, screenshot, or input evidence is inconclusive, write `instrument_error` instead of scoring. If the game itself remains unplayable or cannot show progress after serious adaptive play, record low scores with the observed game-side reason instead of forcing progress.
5. Phase 2 AUDIT: inspect listing metadata, hero/icon/screenshots/video when provided by the work order or reachable from the game page, then score store_listing. Do not change Phase 1 scores after the audit.
6. Save the strict JSON result requested by the work order.
7. Submit with `./bin/playdrop task submit-eval --result-file <path>`.

Do not use `project capture remote`, Playwright CLI, fixed action files, `playdrop project check`, or alternate browser drivers for eval evidence. `playdrop project check` output is development evidence only; never cite it for gameplay or judge conclusions.

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
