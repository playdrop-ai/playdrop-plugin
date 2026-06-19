# Marketing Asset Quality

Use this reference when accepting or rejecting generated marketing images, videos, hero art, and icon art.

## Common Gates

- asset is based on the current playable game
- no menu, loading screen, debug UI, or host chrome is visible
- main action is readable at phone size
- text overlays are short, large, and inside safe zones
- color contrast is strong enough for mobile feeds
- export dimensions match the target family
- final accepted files live under `assets/marketing/`
- final approval has no warning gates, rejected captures, or "pass with caveat" language
- role assets are distinct; PlayDrop hero/icon assets are not reused social thumbnails or covers
- gameplay fills at least 65% of the useful frame for social screenshots and videos
- the first visible promise is in the footage itself, not only in the caption
- accepted packs include visual review contact sheets for source moments, final videos, and final covers/thumbnails
- `marketing-report.json` explains what the viewer understands in one glance and why each selected moment sells the game

## Screenshots And Covers

- never accept a raw frame as the final marketing screenshot
- choose frames with motion, stakes, success, failure, enemies, rewards, or visible progress
- use at most one hook line, not a headline stack, subtitle stack, or paragraph
- do not cover the main character, target, score moment, or reward
- cover images are for platform upload flows; thumbnails are separate exported files
- prefer full-bleed gameplay crops and action close-ups over decorative cards, device frames, or empty backgrounds
- reject frames where the hook text claims a mistake, reward, combo, danger, or win that is not plainly visible
- reject text-dominant covers where the game is background texture for typography
- reject brand + headline + subtitle poster layouts for social covers
- reject dimmed gameplay hidden behind giant type, badges, CTA bars, arrows, or decorative rings
- reject large dead backgrounds around a small or low-contrast game area
- reject one generic layout resized across all platform families
- reject generic hooks that could fit any game unless the frame itself makes the promise obvious
- reject any cover that needs an explanation outside the image to understand the action

## Videos

- action starts at timestamp 0; do not spend the first second on a static title card
- captured game audio is preserved when available and licensed
- final videos are normalized for social playback and must not feel nearly silent
- captions and overlays still communicate the hook while muted
- trim dead time before and after the strongest moment
- avoid rapid cuts that hide how the game is played
- use dynamic crop, zoom, or follow movement around the selected gameplay moment
- the game should feel larger than life in short-form vertical video; do not shrink it into a centered phone/card panel
- avoid large CTA bars, static side columns, generic stock backgrounds, and text-first SaaS layouts
- avoid thumbnails that look like posters for the game instead of a compelling gameplay moment
- the hook must be specific to the visible moment, such as a mistake, save, reward, combo, crash, near miss, boss hit, level clear, unlock, or timed decision
- source captures should be at least 60 fps and 12 seconds; social exports may be 30 or 60 fps depending on target
- every required platform family must be present unless the game does not support that surface

## Hero Art And Icon

- generate or edit hero and icon artwork with PlayDrop AI
- hero art integrates the title/logo, or uses an approved logo reference
- hero art shows the exact game name front and center as large readable title/logo text
- title/logo is exact, readable, and shaped by scene material, light, and perspective
- reject misspelled, warped, extra, clipped, hidden, drawtext-like, or pasted-on title treatment
- reject raw screenshots as icon or hero art
- reject code-drawn listing cards, gameplay composites, thumbnails, and social covers as icon or hero art
- hero art should feature the game name prominently and fit the shipped art direction
- icon art should read clearly at small sizes without depending on tiny text

## Rejection Conditions

- generic artwork that could fit any game
- misleading features or characters not present in the game
- low-resolution or blurry exports
- text clipped by the frame or unreadable on mobile
- missing audio when the declared policy requires audio
- quiet audio that measures or feels unusable for social playback
- source capture produced outside `playdrop project marketing capture`
- first-second footage that is static, generic, or not tied to visible gameplay action
- centered gameplay panel with large dead space around it
- text-dominant poster layout
- brand + headline + subtitle stack on a social cover
- decorative callouts that do not clarify exact gameplay action
- gameplay treated as a dark background texture behind copy
- same cover concept resized across platform families without platform-specific composition
- generic hook text that could fit any game
- CTA-first creative where "play now" is clearer than the actual gameplay
- claimed action that is not visible in the first seconds
- missing visual review contact sheets or report notes
- outputs saved only under `output/` or temporary folders
