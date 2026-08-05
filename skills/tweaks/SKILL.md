---
name: tweaks
description: "Add creator-only in-game controls for PlayDrop Tweaks and preserve creator-tuned values across agent updates."
---

# Tweaks

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use Tweaks for flat runtime settings such as balance numbers, colors, labels, booleans, and enums. Use custom assets for durable content such as levels and race tracks.

- Declare one `tweaks` object in the app's `catalogue.json` with `basedOn`, a flat schema, and complete defaults.
- Read values in game code with `await sdk.tweaks.get()`. The game owns all creator controls.
- Only show save controls when `sdk.creator` is non-null, then replace the complete document with `sdk.creator.replaceTweaks(values)`.
- For an update task, read the latest tweak ID and values from `metadata.playdrop.tweaks` in the provided task context. Outside a task, use `playdrop tweaks get app:creator/name@x.y.z --json`.
- Preserve or deliberately transform the latest values into the next defaults, then set `basedOn` to the latest ID.
- To intentionally remove tweaks, declare `{ "basedOn": "twk_...", "removed": true }`; do not include `schema` or `defaults`.
- Use `playdrop tweaks replace ... --file <path>` only to recover a latest private version whose in-game editor is unusable.

This is the collaboration loop: the creator tunes by feel in the game, then the agent carries those exact values into code as the next defaults. The CLI stops dev, validation, and upload when `basedOn` is stale. Never bypass that error by discarding the creator's values.
