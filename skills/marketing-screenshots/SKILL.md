---
name: marketing-screenshots
description: "Use when a PlayDrop game needs social cover images, promotional screenshots, banners, text overlays, platform-specific image variants, or marketing stills from real capture frames."
---

# Marketing Screenshots

Use this skill after `marketing-capture` has produced source videos.

## Workflow

1. Read `assets/marketing/capture-manifest.json`.
2. Choose strong gameplay frames with action, stakes, or a readable success/fail moment. Do not use title-only or idle frames.
3. Render platform covers and screenshots into `assets/marketing/screenshots/`.
4. Use large simple text, safe zones, and a clear visual hierarchy.
5. Render thumbnail files into `assets/marketing/thumbnails/` where the platform needs separate thumbnails.
6. Update `asset-manifest.json` and `MARKETING.md`.

## Rules

- final screenshots are not raw frames
- cover images are for upload flows like TikTok and Instagram Reels
- thumbnails are standalone files for YouTube, Pinterest, Reddit, X, or Playdrop
- text must remain readable on mobile
- do not cover the main gameplay action
- PlayDrop hero/icon assets are not screenshots; route those to `listing-art`
- do not reuse a social cover as final PlayDrop hero art

## Scripts

Use:

```bash
node <plugin>/scripts/render-marketing-screenshot.ts \
  --root . \
  --input <video.mp4> \
  --out assets/marketing/screenshots/<platform>.png \
  --width 1080 --height 1920 \
  --text "Short hook" \
  --font <font.ttf> \
  --manifest assets/marketing/asset-manifest.json
```

## Shared references

- `marketing-platforms.md`
- `marketing-asset-quality.md`

## Handoff

- source video issues -> `marketing-capture`
- social video variants -> `marketing-videos`
- final copy -> `game-marketing`
