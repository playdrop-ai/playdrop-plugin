# PlayDrop SDK

- Include `https://assets.playdrop.ai/sdk/playdrop.js` for plain HTML.
- Initialize early: `const sdk = await window.playdrop.init()`.
- Log in when the game needs creator/player identity: `await sdk.me.login()`.
- Call `sdk.host.ready()` only after the first designed screen (the board's title or gameplay screen) is fully rendered and, for preview-capable games, after the capture hooks are installed.
- Respect `sdk.host.phase`: preview should show a live representative scene; play should accept input.
- Respect `sdk.host.isPaused`, `onPause`, and `onResume`.
- Gate custom audio on `sdk.host.audioEnabled` and `onAudioPolicyChange`.
- Use `sdk.assets.listAppAssets()` and file roles/content types for declared runtime assets.
- Runtime declarations are promises. If `catalogue.json` declares packs or assets, the game must load and render or play them through the SDK asset manifest.
- Throw clear errors when required assets fail. Do not render hidden fallbacks.
