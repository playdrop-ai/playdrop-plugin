---
name: marketing-screenshots
description: "Use when a PlayDrop game needs social cover images, promotional screenshots, banners, text overlays, platform-specific image variants, or marketing stills from real capture frames."
---

# Marketing Screenshots

Use this skill after `marketing-capture` has produced source videos.

## Workflow

1. Read `assets/marketing/capture-manifest.json`.
2. Choose strong gameplay frames from real captured action, not from menus, idle states, decorative title screens, or generic board states.
3. Crop into the moment so the game action dominates the frame. The cover must read as a game moment first, not as a poster template.
4. Render platform covers and screenshots into `assets/marketing/screenshots/`.
5. Use at most one short hook line, and only when it makes the visible gameplay moment clearer.
6. Render thumbnail files into `assets/marketing/thumbnails/` where the platform needs separate thumbnails.
7. Render a cover/thumbnail contact sheet under `assets/marketing/review/` and inspect it before accepting outputs.
8. Update `asset-manifest.json`, `marketing-report.json`, and `MARKETING.md`.

## Rules

- final screenshots are not raw frames
- cover images are for upload flows like TikTok and Instagram Reels
- thumbnails are standalone files for YouTube, Pinterest, Reddit, X, or Playdrop
- text must remain readable on mobile
- do not cover the main gameplay action
- do not make the cover text-dominant; if the first read is the headline instead of the game moment, reject it
- do not dim the game into background texture behind a giant title, headline, subtitle, badge, CTA, or feature stack
- do not use brand + headline + subtitle stacks for social covers
- do not use decorative arrows, rings, badges, stickers, glows, or callouts unless they clarify the exact visible gameplay action
- do not use large dead backgrounds around a small game panel
- do not use a generic card, phone mockup, or SaaS-style frame when a full-bleed gameplay crop would be stronger
- do not reuse one cover layout across every platform; each crop must fit that platform's reading pattern
- reject generic hooks like "Save the run", "Play now", "Daily streak", or "Beat the clock" unless the selected frame makes that promise obvious without reading the caption
- gameplay should fill at least 65% of the useful frame
- thumbnails and covers must declare why the selected frame sells the game and what the viewer understands in one glance
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
  --viewer-promise "The viewer understands the risk and payoff in one glance" \
  --selected-frame-reason "The hazard, player action, and consequence are all visible" \
  --composition action-closeup \
  --gameplay-fill 0.78 \
  --zoom 1.15 \
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
