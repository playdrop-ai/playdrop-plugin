---
name: marketing-pack
description: "Use when a PlayDrop creator asks to prepare marketing, make a launch kit, create promo assets, create social videos, create marketing screenshots, package listing media, or prepare a game for promotion."
---

# Marketing Pack

Use this skill for the single-prompt workflow:

```text
let's prepare the marketing for my game
```

This skill orchestrates specialist skills. It should not duplicate platform specs or rendering details.

## Workflow

1. Run `gameplay-review` first. If the game is not ready to market, hand off to `game-improvement` and edit by default.
2. Run `catalogue-preview` to make `catalogue.json` previewable and capture-ready.
3. Run `marketing-capture` to produce real local captures under `assets/marketing/`.
4. Run `marketing-screenshots`, `marketing-videos`, and `listing-art` after captures exist. These can run independently.
5. Run `store-listing` for Playdrop listing readiness.
6. Run `game-marketing` to write `MARKETING.md`.
7. Run `node <plugin>/scripts/validate-marketing-manifest.ts --root .`.
8. Re-run `playdrop project validate .`.

## Rules

- edit the creator project by default when the prompt asks to prepare marketing
- accepted assets live in `assets/marketing/`, not `output/`
- temporary files may live in `tmp/marketing/`
- update `catalogue.json` automatically after validation
- only touch creator project files while operating on a creator game
- stop at the first gate that cannot be fixed clearly
- do not use hosted capture, server capture, or remote capture
- do not produce raw screenshots or raw videos as final marketing assets
- long-form YouTube is out of scope unless the user explicitly asks for longer capture

## Shared references

- `preview-guidelines.md`
- `marketing-capture.md`
- `marketing-platforms.md`
- `marketing-audio.md`
- `marketing-asset-quality.md`

## Handoff

- preview metadata or preview runtime hooks -> `catalogue-preview`
- local capture -> `marketing-capture`
- covers and screenshots -> `marketing-screenshots`
- social videos and thumbnails -> `marketing-videos`
- hero artwork and icon artwork -> `listing-art`
- Playdrop listing package -> `store-listing`
- copy and distribution plan -> `game-marketing`
