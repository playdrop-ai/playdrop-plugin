---
name: make-social-media-package
description: "Package approved PlayDrop game marketing media for YouTube, TikTok, Instagram, and X. Use for a game marketing package, channel-ready landscape and portrait videos, four-image Instagram stories, publishing copy, destination mappings, or a final social-media readiness audit."
---

# Make Social Media Package

Map approved game marketing media to YouTube, TikTok, Instagram, and X. Reuse canonical files instead of creating channel copies.

## Preconditions

- Read `../../references/marketing-creative-production.md`.
- Inspect the playable game, listing, approved four-image story, and approved video edits.
- Use `../market-game/SKILL.md` when the promise or selling points are unclear.
- Use `../make-marketing-screenshots/SKILL.md` or `../make-marketing-video/SKILL.md` when required source media is missing.

Fail with `social_media_source_missing` rather than writing `null`, `pending`, or notes in place of required media.

## Standard package

Create `assets/marketing/social-media/manifest.json` that maps:

- the approved 16:9 landscape trailer to YouTube and X;
- the approved 9:16 portrait short to YouTube Shorts, TikTok, Instagram Reels, and Instagram Stories;
- the four approved 9:16 selling-point images to Instagram in their established order;
- channel-ready YouTube `trailerTitle`, `shortTitle`, and `description`, TikTok and Instagram `caption`, X `copy`, and the canonical PlayDrop URL.

Keep the canonical assets in their approved locations and reference them from the manifest. Do not duplicate identical files into platform folders.

Add Pinterest, covers, thumbnails, feed-video derivatives, or another channel only when the user requests them.

## Rules

- Keep the 9:16 short around 12 seconds.
- Keep the 16:9 trailer between 30 and 60 seconds without filler.
- Preserve synchronized game audio, input cues, selling-point plates, semantic edit boundaries, and per-phase speeds.
- Preserve each approved image's complete headline and selling point.
- Do not crop meaningful gameplay or text. Recapture or generate a native destination ratio when needed.
- Keep claims grounded in the shipped game.

## Validate

Run:

```bash
node scripts/validate-social-package.mjs <game>/assets/marketing/social-media
```

Then inspect both videos completely and the four images at full and thumbnail size. Technical validation cannot prove that timing, framing, copy, or gameplay is compelling.

## Completion bar

- YouTube, TikTok, Instagram, and X map the correct canonical assets.
- The landscape trailer and portrait short pass the video skill's technical and visual review.
- Instagram contains exactly four ordered portrait selling-point images.
- The manifest includes channel-ready copy and the canonical destination URL.
- Nothing has been uploaded or published.
