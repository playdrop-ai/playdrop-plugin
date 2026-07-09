---
name: task-worker
description: "Use inside PlayDrop worker task workspaces for progress, upload, completion, failure, next steps, and task safety rules."
---

# Task Worker

Use this only when the prompt provides `./bin/playdrop task ...` commands.

## Protocol

- Use `./bin/playdrop`, not a global `playdrop` binary.
- If command syntax is unclear, use read-only help such as `./bin/playdrop help search` or `./bin/playdrop project check --help`.
- Report meaningful progress with done and current state:
  `./bin/playdrop task report --phase <phase> --done "<what changed>" --current "<what is happening now>"`.
- Report the catalogue plan after `catalogue.json` has the intended app entry:
  `./bin/playdrop task report-catalogue --file catalogue.json --message "Planned the version"`.
- Validate before upload: `./bin/playdrop project validate .` and `./bin/playdrop project check .`.
- Upload only when the version is final for this task: `./bin/playdrop task upload`.
- Finish with `./bin/playdrop task done --summary "<one-sentence creator recap>" --next-steps next-steps.json`.
- Write the summary as a chat reply to the creator, naming what you built with no jargon, for example: "Your neon courier runner is ready: dodge the sparks and chase your best score."
- If blocked by tooling, access, validation, or an impossible request, run `./bin/playdrop task fail --message "<creator-friendly reason>"`.

## Next Steps

Write `next-steps.json`:

```json
{
  "nextSteps": [
    {
      "id": "tune-difficulty",
      "title": "Tune difficulty",
      "description": "Make the opening easier and add a sharper ramp after the player understands the loop.",
      "prompt": "Tune the game difficulty so the first minute is approachable and the second minute becomes meaningfully harder.",
      "category": "MECHANICS"
    }
  ]
}
```

Use 0-3 entries. Categories: `POLISH`, `CONTENT`, `MECHANICS`, `VISUALS`, `AUDIO`, `MONETIZATION`, `PUBLISHING`.

## Boundaries

- Do not publish publicly from a task.
- Do not read credentials, platform source, admin sessions, Slack tokens, or unrelated projects.
- Do not stop after upload; close the task with done or fail.
- Do not silently substitute degraded output. Fix the issue or fail clearly.
