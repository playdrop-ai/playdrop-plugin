---
name: listing-art
description: "Use when a PlayDrop game needs AI-generated final listing art, app icon artwork, hero artwork, title typography composited from real font assets, or final store art validation."
---

# Listing Art

Use this skill for final Playdrop hero artwork and app icon artwork.

## Workflow

1. Use real capture frames and any `art-direction` sheet as references.
2. Generate or edit the base hero artwork with Playdrop AI image generation.
3. Validate the generated artwork before typography compositing.
4. Composite the game title with a real project font or a newly added licensed font.
5. Generate icon artwork as a separate square composition and normalize it to a square icon file.
6. Save accepted assets under `assets/marketing/playdrop/`.
7. Update `asset-manifest.json`, `catalogue.json`, and `MARKETING.md`.

## Rules

- artwork must be AI-generated or AI-edited, not code-drawn
- title text must be composited with a real font asset
- do not trust image generation to render the game title correctly
- do not use raw screenshot crops as icon or hero art
- reject generic, unreadable, low-quality, or misleading art
- low-quality hero art is a Playdrop rejection condition
- validate artwork quality before spending time on title compositing

## Scripts

Use:

```bash
node <plugin>/scripts/compose-listing-title.ts \
  --root . \
  --input assets/marketing/playdrop/hero-art.png \
  --out assets/marketing/playdrop/hero-title.png \
  --title "Game Name" \
  --font <font.ttf> \
  --manifest assets/marketing/asset-manifest.json

node <plugin>/scripts/compose-listing-icon.ts \
  --root . \
  --input assets/marketing/playdrop/icon-art.png \
  --out assets/marketing/playdrop/icon.png \
  --manifest assets/marketing/asset-manifest.json
```

## Shared references

- `art-direction.md`
- `marketing-asset-quality.md`

## Handoff

- early visual exploration -> `art-direction`
- final listing package -> `store-listing`
