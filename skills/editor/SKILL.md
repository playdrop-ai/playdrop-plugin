---
name: editor
description: "Add an optional, game-specific PlayDrop creator Editor that runs from the hosted bundle in the owner-only editor phase."
---

# PlayDrop Creator Editor

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use this skill only when the creator asks to add an Editor or when an Editor task is attached to the game.

An Editor is not a generic visual or source-code editor. It is a focused owner-only surface built for the current game, such as a level builder, balance panel, asset chooser, dialogue editor, track builder, or spritesheet correction tool.

## Contract

1. Set `editorSupported: true` on the hosted app entry in `catalogue.json`. External apps cannot declare Editor support.
2. Use the same hosted bundle as Playtest. Select Editor UI when `sdk.host.phase === 'editor'` and keep normal gameplay behavior for `play` and `preview`.
3. Call `sdk.host.editorReady()` after the Editor UI is mounted and can accept creator input. A normal `sdk.host.ready()` signal does not satisfy the Editor delivery check.
4. Mount the Editor from local game state before reading `sdk.creator`, then call `editorReady()`. The staged Editor boot check intentionally has no creator APIs because the version is not finalized yet. Initialize `sdk.creator` lazily when a save, note, or asset action needs it, and throw `creator_tools_unavailable` only for that action.
5. Use Tweaks for flat values. Use Playtest Notes for structured exports and files that the agent must integrate. Use custom assets for durable typed game content.
6. Subscribe to `sdk.host.onPhaseChange(...)`. Mount the Editor when the phase becomes `editor`, dispose or hide its controls when the phase becomes `play` or `preview`, and call `sdk.host.editorReady()` again after every Editor mount. Call `sdk.host.ready()` after Playtest or Preview is mounted again. Studio changes phase on the existing iframe, so an Editor that only checks the initial phase is invalid.
7. Preserve pause, resume, surface resize, and audio policy behavior. The Studio may keep the runtime mounted but paused behind another tab.
8. Validate the normal Playtest path and the Editor-phase boot before delivery. The Editor-phase check must render the Editor and emit `editorReady()` without requiring Tweaks, Notes, or asset requests during startup.

Keep the Editor small and purpose-built. Do not add a scene graph, code editor, plugin system, or generic inspector unless the game itself needs that exact tool now.
