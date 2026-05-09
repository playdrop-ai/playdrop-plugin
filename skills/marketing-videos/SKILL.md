---
name: marketing-videos
description: "Use when a PlayDrop game needs TikTok, Instagram, YouTube Shorts, Snapchat, Pinterest, YouTube, X, Reddit, Facebook, LinkedIn, social video variants, covers, captions, or thumbnails."
---

# Marketing Videos

Use this skill after `marketing-capture` has produced source videos.

## Workflow

1. Read `assets/marketing/capture-manifest.json`.
2. Create vertical, landscape, feed portrait, and square variants only for relevant surfaces.
3. Keep the strongest motion in the first 1 to 2 seconds.
4. Preserve captured game audio unless the platform export is intentionally silent.
5. Render separate thumbnails where needed.
6. Update `asset-manifest.json` and `MARKETING.md`.

## Rules

- final social videos are not raw captures
- short vertical covers TikTok, Instagram Reels, Instagram Stories, YouTube Shorts, Snapchat, and Pinterest
- short landscape covers YouTube, X, Reddit, and web embeds
- long-form YouTube is out of scope unless the user explicitly asks for a longer capture
- text overlays must work when muted
- do not add unlicensed commercial music or platform-trending audio
- use captured game music and SFX from the preview whenever the audio policy allows it

## Scripts

Use:

```bash
node <plugin>/scripts/render-marketing-video.ts \
  --root . \
  --input <capture.mp4> \
  --out assets/marketing/social/<platform>.mp4 \
  --width 1080 --height 1920 \
  --text "Short hook" \
  --font <font.ttf> \
  --thumbnail-out assets/marketing/thumbnails/<platform>.png \
  --manifest assets/marketing/asset-manifest.json
```

## Shared references

- `marketing-platforms.md`
- `marketing-audio.md`
- `marketing-asset-quality.md`

## Handoff

- cover images -> `marketing-screenshots`
- social copy -> `game-marketing`
