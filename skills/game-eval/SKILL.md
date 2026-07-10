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
- Wake the host display at most once, before the browser session starts. Never wake, re-wake, or re-focus the host between captures or during play.
- Do not scan the host recursively. Read only the task workspace and the staged plugin files named here.
- If tooling, access, validation, or submission fails, run `./bin/playdrop task fail --message "<clear operational reason>"`.

## Browser evidence surface

The judge has exactly one browser evidence surface: the controlled Claude Code `--chrome` gameplay tab. Every scored observation and every screenshot comes from that one tab.

- Capture first-frame, core, win or progression, and loss or failure with the built-in Claude Chrome computer screenshot action.
- Never open an artifact window, never use `open -na`, never use `playdrop review list-windows`, and never use `playdrop review screenshot`. The native recorder is listing capture only and is not judge evidence.
- Each built-in screenshot returns a distinct `ss_...` id. All four captures for a target must come from the same controlled tab and must use four distinct screenshot ids.

The worker reads the screenshot bytes directly from the Claude stream-json output, writes the named PNGs and `instrument-evidence.json` into the target evidence directory, and submission verifies the screenshot id, tool-use id, tab id, source and file hashes, and decoded pixels against the immutable server transcript. A second evidence surface is therefore structurally invalid and cannot be submitted.

Use one evidence directory per target, and pass the target id as the evidence group:

```bash
./bin/playdrop task evidence --group target-1 --name core --screenshot-id ss_example --evidence-dir .tmp/evidence
```

Repeat with `--name first-frame`, `--name win`, and `--name loss`, each with its own distinct `ss_...` id, for every target.

## References

Read the staged references before scoring:

- `.playdrop/plugin/references/game-review-evidence-capture.md`
- `.playdrop/plugin/references/game-review-rating-scale.md`
- `.playdrop/plugin/references/game-review-score-caps.md`
- `.playdrop/plugin/references/dimensions.md`
- `.playdrop/plugin/references/quality-bars.md`

## Workflow

1. Read the task work order and identify every target id, creator prompt, launch URL, and primary surface hint.
2. Phase 1 PLAY: open each launch URL with Claude Code `--chrome` attached to the work Chrome profile, play adaptively, and score request_fidelity, core_loop_fun, controls, polish, and stability from player experience only. The tab you open for a target is that target's controlled tab.
3. Run the browser canary before scoring: know the exact expected host GPU renderer string recorded for this machine, record the actual WebGL renderer string in evidence, require an exact match to the expected string, verify one click with visible effect, verify one relevant key press with visible effect, and take a nonblank built-in screenshot of the controlled tab. The expected renderer string is supplied by the work order or worker environment for this machine; never infer it from local files and never match a shortened form, only the full recorded string exactly. If the expected value is missing, the actual renderer mismatches, SwiftShader appears, or any other canary step fails, exit with `instrument-error` instead of scoring.
4. Save Phase 1 evidence from the controlled tab: first-frame, core, win or progression, and loss or failure, persisted with `task evidence` into that target's evidence directory as each capture is taken. Write the Phase 1 notes immediately once evidence is sufficient. If browser control, renderer, screenshot, or input evidence is inconclusive, exit with `instrument-error` instead of scoring. If the game itself remains unplayable or cannot show progress after serious adaptive play, record low scores with the observed game-side reason instead of forcing progress.
5. Phase 2 AUDIT: inspect listing metadata, hero/icon/screenshots/video when provided by the work order or reachable from the game page, then score store_listing. Do not change Phase 1 scores after the audit.
6. Save the strict JSON result requested by the work order.
7. Close every tab and window this task opened, including every controlled Claude `--chrome` tab, and leave exactly one blank Chrome window. Leave pre-existing user tabs alone. AppleScript or `osascript` is allowed only for this final cleanup, never for gameplay or input. If cleanup fails, include the cleanup error in the final status.
8. Submit with `./bin/playdrop task submit-eval --result-file <path> --evidence-dir <target-1-dir> <target-2-dir>`, passing one evidence directory per target. This is the final operation. Perform no browser operation after it.

## Instrument failure

Instrument failure is a first-class exit and is never a game score. After browser cleanup, exit with:

```bash
./bin/playdrop task instrument-error --reason renderer
```

Use `renderer`, `browser_control`, or `screenshot` for failures you observe. Reviewer bootstrap failure or an auth or sign-in wall is terminated automatically by the shell as `instrument_error(auth_state)`; stop there. Never score such a run, never sign in, never inspect tokens, and never hunt for bypasses. Like submission, `instrument-error` is the final operation, and no browser operation follows it.

Do not use `project capture remote`, Playwright CLI, fixed action files, `playdrop project check`, AppleScript, `osascript`, `cliclick`, CGEvent tools, JavaScript input injection, or alternate browser drivers for eval decisions. If Claude Code `--chrome` cannot create the required visible input effect with ordinary browser clicks, taps, and key presses, exit with `instrument-error` instead of switching tools. `playdrop project check` output is development evidence only; never cite it for gameplay or judge conclusions.

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
