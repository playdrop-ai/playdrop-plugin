---
name: make-social-media-package
description: "Package approved PlayDrop game marketing media for YouTube, TikTok, Instagram, Pinterest, and X. Use when a game needs channel-ready social videos, static Pins, Instagram carousels, thumbnails, covers, publishing copy, aspect-ratio adaptations, or a final social-media readiness audit."
---

# Make Social Media Package

Turn approved game marketing media into one small, reusable social package. Reuse strong footage and campaign art instead of inventing new content for every network.

## Preconditions

- Read `../../references/marketing-creative-production.md`. It defines the
  shared protected-art, gameplay-truth, caption, geometry, phase-edit, and
  review contract.
- Inspect the playable game, listing, hero art, approved screenshot story, and approved video edits.
- Use `../market-game/SKILL.md` when the audience or player promise is unclear.
- Use `../make-marketing-screenshots/SKILL.md` or `../make-marketing-video/SKILL.md` when approved source media is missing.
- Read `references/platform-formats.md` and reopen the linked official sources before final export.

Fail with `social_media_source_missing` when approved real gameplay and campaign art are unavailable.

## MVP package

Create this package unless the user narrows the channels:

```text
social-media/
  manifest.json
  short/
    portrait-9x16.mp4
    pinterest-2x3.mp4
  trailer/
    landscape-16x9.mp4
  pinterest/
    static/
      01-hero.png
      02-*.png
      03-*.png
      04-*.png
      05-*.png
  instagram/
    reels-cover-420x654.png
    feed/
      video-3x4.mp4
      carousel/
        01-hero.png
        02-*.png
        03-*.png
        04-*.png
        05-*.png
  youtube/
    trailer-thumbnail-1280x720.png
```

Reuse the shared 9:16 short for YouTube Shorts, TikTok, Instagram Reels, and Instagram Stories. Reuse the 16:9 trailer for YouTube and X. Do not duplicate identical files into platform folders.

## Geometry

Apply the geometry contract in `../../references/marketing-creative-production.md` to every derivative: uniform scale only, empty-margin crops only, no bars, gutters, stretching, or fill, and native 3:4 and 2:3 for width-filling games. If a crop removes meaningful content, regenerate the still or recapture the video at the destination ratio. Package-specific rules:

- Replace a channel-inappropriate end card with a clean ratio-specific hero ending rather than cropping its CTA or logo.
- Use protected hero and end-card files unchanged; when no ratio-native asset exists, use real gameplay.
- Keep sample aspect ratio at `1:1`.

## Workflow

### 1. Confirm the shared story

- Keep one mechanic-to-payoff short at roughly 10 to 15 seconds.
- Keep one landscape trailer around 20 to 30 seconds.
- Reuse the approved four-image screenshot story: core action, tension, payoff, and goal. Use fewer images only when the game has fewer truthful selling points. Use the protected hero separately when the channel plan calls for an identity card.
- Keep text, touch cues, and game identity clear without sound.

### 2. Adapt the videos

- Export the shared short at 1080 x 1920.
- Export the Pinterest short at 1000 x 1500 from a native 2:3 capture or a
  verified safe crop that removes empty margin only.
- Export the Instagram feed cut at 1080 x 1440 from a native 3:4 capture or a
  verified safe crop that removes empty margin only.
- Export the landscape trailer at 1920 x 1080.
- Keep the original music and synchronized input cues.
- Preserve the approved caption plates, interaction system, semantic segment
  boundaries, and per-phase playback speeds. Do not rebuild them with generic
  text or apply one speed to the entire derivative.
- Inspect the opening, action, payoff, and ending of every ratio. Do not approve a crop by checking only its first frame.

### 3. Adapt the stills

- Create five 1000 x 1500 Pinterest image Pins: hero plus the four approved campaign beats.
- Create the matching five-card 1080 x 1440 Instagram feed carousel.
- Use image editing to create native 2:3 and 3:4 compositions from the closest canonical 9:16 master when a crop would remove gameplay or text.
- Derive one social still ratio from another only after a side-by-side crop preview proves that the removed region contains empty scenery.
- Create a 420 x 654 Instagram Reel cover from approved hero art.
- Create a 1280 x 720 YouTube trailer thumbnail from approved landscape hero art.
- Keep every headline fully visible. Do not rebuild approved typography unless cropping cannot preserve it.

### 4. Write the manifest

Record:

- destination URL,
- file mapping for every platform,
- ordered carousel and Pin files,
- YouTube titles and description,
- TikTok and Instagram captions,
- Pinterest titles and description,
- X copy.

Keep titles concrete and searchable. Keep claims grounded in the shipped game.

`manifest.json` is the publishing handoff. It owns approved assets, copy, and
destination mappings. The private publisher reads it and creates the sibling
`publication.json` only when publishing starts. Do not put provider results,
timestamps, metrics, or mutable publication state in `manifest.json`.

### 5. Validate

Run:

```bash
node scripts/validate-social-package.mjs <game>/assets/marketing/social-media
```

Then visually inspect per the reference's review-evidence section: every still at full and thumbnail size, every video's opening, payoff, and ending, frames around every cue and speed boundary, protected pixels against their canonical source, and one delivery-order composite. Also check text and action against TikTok and Instagram UI safe zones. Metadata validation cannot prove a crop is visually honest; the visual review is mandatory.

## Completion bar

- YouTube, TikTok, Instagram, Pinterest, and X have an explicit asset mapping.
- Pinterest includes a real 2:3 video and static image Pins; Instagram includes the shared Reel and Story video, a Reel cover, a 3:4 feed video, and a static carousel.
- The reference's geometry and protected-asset contracts hold, and approved caption systems remain unchanged.
- Every file passes technical validation and visual review.
- The package includes channel-ready copy and the canonical destination URL.
- Nothing has been uploaded or published.
