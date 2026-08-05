---
name: playtest-notes
description: "Add creator-only in-game Playtest Notes and consume creator-authored feedback when updating a PlayDrop game."
---

# Playtest Notes

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Games can use `sdk.creator.notes` to let their creator capture text, images, JSON, Markdown, logs, and exact asset references while playtesting. The agent integrates the game-owned UI; only the creator authors notes through it.

Use the exact typed draft shapes. Text is `{ kind: 'TEXT', text }`; JSON is `{ kind: 'JSON', value }`. Kinds are uppercase, there is no `title` field, and game code must not cast the SDK to `any` to bypass these contracts.

- Auto and Local Agent tasks receive selected notes automatically through the update prompt and task inputs.
- Pending notes retain the app version where they were authored and remain available across later app versions until consumed or cleared.
- When working with Codex, Claude Code, or another external agent, inspect the exact app version with `playdrop notes browse app:creator/name@x.y.z --json`.
- Use `--output <directory>` when note attachments must be materialized locally.
- Clear only the explicit note IDs you actually incorporated, and only after completing that work.
- Do not clear removed, unrelated, or unread notes.

Use the SDK and CLI help as the API reference.
