---
name: catalogue-preview
description: "Use when a PlayDrop game needs previewable catalogue metadata, preview-mode runtime hooks, no-HUD autoplay preview scenes, seeded preview states, preview audio policy, or capture-ready moments."
---

# Catalogue Preview

Use this skill before capture or listing work when a game needs a real Playdrop preview.

## Workflow

1. Inspect `catalogue.json`.
2. Set the app entry to `previewable: true`.
3. Add `preview.audioPolicy`; use `music-and-sfx` by default.
4. Confirm the game implements `window.__listingCapture.prepare(payload)`.
5. For `music-and-sfx` or `sfx-only`, confirm the game also implements `window.__listingCapture.startAudioCapture()` and `window.__listingCapture.stopAudioCapture()`.
6. Confirm preview mode hides menus, debug UI, host UI, and nonessential HUD.
7. Confirm the first seconds contain motion, stakes, effects, scoring, danger, success, or another exciting moment.
8. Confirm the first 12 seconds include at least two distinct sellable moments so the video skill can cut into real action instead of inventing copy.
9. Add or fix background music and SFX using PlayDrop catalogue audio or PlayDrop AI generation when the game lacks marketing-ready audio.
10. Confirm preview music and SFX match the declared audio policy and are loud enough for social playback.
11. Re-run `playdrop project validate .`.

## Runtime contract

The preview hook receives:

```ts
{
  active: true,
  sceneId: "listing-landscape" | "listing-portrait" | string,
  surface: "desktop" | "mobile-landscape" | "mobile-portrait",
  seed: string,
  audioPolicy: "music-and-sfx" | "sfx-only" | "silent"
}
```

## Rules

- implement the preview hook when missing
- implement preview audio capture hooks when the audio policy is not `silent`
- use a seed or scripted scene for repeatable capture
- update `catalogue.json` automatically when preview metadata is validated
- do not treat a menu, loading screen, or normal play start as a marketing preview
- do not accept a preview that requires text to explain why it is exciting; the footage needs visible cause and effect
- `music-and-sfx` is the default for marketing because the same preview audio is captured into social videos
- `sfx-only` is allowed only when the game intentionally has no music and `MARKETING.md` explains why
- `silent` must be intentional and explained in `MARKETING.md`
- no hosted capture or server capture assumptions

## Shared references

- `preview-guidelines.md`
- `marketing-audio.md`
- `sdk-integration.md`

## Handoff

- missing visual/audio quality -> `game-improvement`
- capture-ready preview -> `marketing-capture`
