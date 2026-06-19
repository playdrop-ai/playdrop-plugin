---
name: listing-art
description: "Use when a PlayDrop game needs final AI listing art, app icon artwork, hero artwork, title/logo treatment, or store art validation."
---

# Listing Art

Use this skill for final PlayDrop hero and app icon artwork.

## Workflow

1. Use real capture frames, runtime assets, and any `art-direction` sheet as references.
2. Generate or AI-edit final hero artwork that includes the exact game title/logo front and center.
3. Make the title/logo part of the scene artwork, material, lighting, and perspective, not a later text overlay.
4. Validate title spelling, readability, and art quality before accepting.
5. Generate icon art as a separate PlayDrop AI image, never as a hero crop.
6. Save accepted files under `assets/marketing/playdrop/`.
7. Update `asset-manifest.json`, `catalogue.json`, and `MARKETING.md`.

## Rules

- artwork must be AI-generated or AI-edited, not code-drawn
- when running inside a staged PlayDrop worker task, use PlayDrop AI image generation directly for final hero files:
  ```bash
  ./bin/playdrop ai create image "<prompt including the exact game title>" \
    --ratio 9:16 --size 1K \
    --output assets/marketing/playdrop/hero-portrait.png

  ./bin/playdrop ai create image "<prompt including the exact game title>" \
    --ratio 16:9 --size 1K \
    --output assets/marketing/playdrop/hero-landscape.png
  ```
- each hero prompt must include the exact game display name as large readable title/logo text, front and center, integrated into the artwork
- each hero prompt must forbid all extra readable text, words, letters, numbers, banners, signs, captions, UI labels, dates, taglines, subtitles, celebration text, and decorative signage anywhere else in the image
- safe hero wording: `PlayDrop hero artwork for "<Exact Game Display Name>" with the exact title "<Exact Game Display Name>" as large readable front-and-center title/logo text integrated into the scene. No extra readable text, words, letters, numbers, banners, signs, captions, UI labels, dates, taglines, subtitles, or decorative signage anywhere else in the image.`
- the final hero paths must be `assets/marketing/playdrop/hero-portrait.png` and `assets/marketing/playdrop/hero-landscape.png`; do not hand-copy, hand-edit, re-export, or add text after PlayDrop AI generation because upload validation checks the PlayDrop AI prompt metadata on the final PNGs
- if `./bin/playdrop ai create image --output` is unavailable or does not produce a valid PNG with PlayDrop prompt metadata, stop with a clear error instead of creating replacement PNGs through another tool
- final hero art must use the exact game title/logo lockup, unless an approved logo asset already exists
- title/logo must be exact, front and center, prominent, readable at listing scale, and integrated with the scene material, light, and perspective
- reject misspelled, warped, clipped, small, or partially hidden title text
- reject any extra readable text anywhere in the image, even if it is decorative signage, a party banner, a label, a date, a subtitle, or a background word
- reject plain drawtext-style overlays or pasted-on title treatment for final PlayDrop hero art
- do not use raw screenshot crops as icon or hero art
- do not use social covers, thumbnails, gameplay screenshots, code-drawn composites, or template cards as final hero/icon art
- do not proceed when Playdrop AI image generation is unavailable; stop or fix the AI generation path
- the icon, portrait hero, and landscape hero must be distinct listing assets, not byte-identical reused social outputs
- reject generic, unreadable, low-quality, or misleading art

## Scripts

Use icon normalization after accepting AI icon art:

```bash
node <plugin>/scripts/compose-listing-icon.ts \
  --root . \
  --input assets/marketing/playdrop/icon-art.png \
  --out assets/marketing/playdrop/icon.png \
  --artwork-source playdrop-ai \
  --manifest assets/marketing/asset-manifest.json
```

For worker-task final hero art, final PNG metadata must come directly from `./bin/playdrop ai create image --output` on `hero-portrait.png` and `hero-landscape.png`.

## Shared references

- `art-direction.md`
- `marketing-asset-quality.md`

## Handoff

- early visual exploration -> `art-direction`
- final listing package -> `store-listing`
