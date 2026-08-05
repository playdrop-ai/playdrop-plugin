# PlayDrop SDK

- Include `https://assets.playdrop.ai/sdk/playdrop.js` for plain HTML.
- Initialize early: `const sdk = await window.playdrop.init()`.
- Never prompt for login during initialization. Read `sdk.me.isLoggedIn` and subscribe with `sdk.me.onAuthChange(...)`; only call `sdk.me.promptLogin()` from an explicit user action when the game uses multiplayer, purchases, profiles, or other account features.
- Always call app saves, achievement writes, and leaderboard submissions directly. Never gate them on `sdk.me.isLoggedIn`; logged-out calls safely do not persist, while private guest and real-account calls persist under the hood.
- Call `sdk.host.ready()` only after the first designed screen (the board's title or gameplay screen) is fully rendered and, for preview-capable games, after the capture hooks are installed.
- Respect `sdk.host.phase`: preview should show a live representative scene; play should accept input.
- Respect `sdk.host.isPaused`, `onPause`, and `onResume`.
- Gate custom audio on `sdk.host.audioEnabled` and `onAudioPolicyChange`.
- Use `sdk.assets.listAppAssets()` and file roles/content types for declared runtime assets.
- Runtime declarations are promises. If `catalogue.json` declares packs or assets, the game must load and render or play them through the SDK asset manifest.
- Throw clear errors when required assets fail. Do not render hidden fallbacks.
- Read declared tweak values with `await sdk.tweaks.get()`. When `sdk.creator` is non-null, game-owned creator UI may replace the complete value document with `sdk.creator.replaceTweaks(values)`.
- When `sdk.creator` is non-null, game-owned playtest UI may use `sdk.creator.notes.list()`, `add(note)`, `replace(id, note)`, and `remove(id)` for text, Markdown, JSON, image, log, or exact asset-reference notes.
- Playtest note kinds are uppercase and have exact payload shapes. For example: `await sdk.creator.notes.add({ kind: 'TEXT', text: 'Jump feels weak' })` and `await sdk.creator.notes.add({ kind: 'JSON', value: { gravity: 900 } })`. There is no `title` field. Keep the typed SDK value instead of casting `sdk` or `sdk.creator` to `any`, so invalid note payloads fail validation.
