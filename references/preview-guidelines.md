# Preview Guidelines

Use this reference when making `catalogue.json` previewable and capture-ready.

## Catalogue Metadata

The app entry should include:

```json
{
  "previewable": true,
  "preview": {
    "audioPolicy": "music-and-sfx"
  }
}
```

Allowed `audioPolicy` values are `music-and-sfx`, `sfx-only`, and `silent`.

## Runtime Hook

The game should expose:

```ts
window.__listingCapture = {
  async prepare(payload) {
    // Set seed, surface, scene, HUD state, and audio state.
  }
}
```

The payload contains:

```ts
{
  active: true,
  sceneId: string,
  surface: "desktop" | "mobile-landscape" | "mobile-portrait",
  seed: string,
  audioPolicy: "music-and-sfx" | "sfx-only" | "silent"
}
```

For non-silent audio policies, the hook must also support preview audio capture:

```ts
window.__listingCapture.startAudioCapture?.()
window.__listingCapture.stopAudioCapture?.()
```

`stopAudioCapture` should return an object with `mimeType` and base64 audio data.

## Scene Requirements

- hide menus, debug UI, host UI, corner watermarks, and nonessential HUD
- skip loading screens and onboarding
- show action, danger, scoring, effects, progression, win, fail, or a strong mechanic quickly
- set a seed or scripted state for repeatable captures
- keep text and gameplay readable on portrait, landscape, and desktop surfaces
- preserve real controls and game visuals instead of staging a misleading scene

## Catalogue Updates

The marketing workflow may update `catalogue.json` automatically with preview metadata, listing media paths, tags, listing title, short description, and long description after validation.
