---
name: game-marketing
description: "Use when a PlayDrop game needs MARKETING.md, PlayDrop listing copy, social captions, platform-specific posting guidance, tags, descriptions, link sticker text, GitHub SEO, boosts, or distribution planning."
---

# Game Marketing

Use this skill after the game, preview, capture, and listing assets are strong enough to promote.

## Workflow

1. Confirm `assets/marketing/capture-manifest.json`, `asset-manifest.json`, and `marketing-report.json` exist.
2. Confirm `marketing-report.json` includes `visualReview.sourceMomentContactSheet`, `visualReview.finalVideoContactSheet`, `visualReview.finalCoverContactSheet`, and visual review notes.
3. Run `node <plugin>/scripts/validate-marketing-manifest.ts --root .` before writing final approval language.
4. Include PlayDrop listing title, short description, long description, tags, and listing asset map.
5. Include per-platform file maps, captions, descriptions, hashtags, link sticker text, thumbnails, cover notes, and posting notes.
6. Include audio source notes and any intentionally skipped outputs with reasons.
7. Improve GitHub and public share surfaces only after the asset plan is complete.

## Shared references

- `github-seo.md`
- `boosts.md`
- `platform-capabilities.md`
- `marketing-platforms.md`
- `marketing-audio.md`

## MARKETING.md Required Sections

- PlayDrop Listing
- Asset File Map
- Platform Posting Plan
- Copy Bank
- Audio Sources
- Skipped Outputs
- Validation Notes

## Rules

- do not treat marketing as a substitute for weak product or listing quality
- keep accepted asset paths under `assets/marketing/`
- write copy for the actual current game, not a more ambitious version of it
- explain reused files across platforms instead of duplicating assets unnecessarily
- do not write "PASS with caveat", "WARNING", or similar approval language for required gates
- failed or skipped required gates belong in a blocking action list, not in a finished marketing plan
- do not call a pack finished when visual review contact sheets or one-glance review notes are missing
- social copy should sell the game to players; process/dev copy is only for an explicitly developer-facing LinkedIn post

## Handoff

- weak listing or unclear public positioning -> `store-listing`
- product, runtime, or polish gaps -> `game-improvement`
- service or platform feature gaps -> `service-integration`
- missing source captures -> `marketing-capture`
