# Marketing Asset Quality

Use this reference when accepting or rejecting generated marketing images, videos, hero art, and icon art.

## Common Gates

- asset is based on the current playable game
- no menu, loading screen, debug UI, or host chrome is visible
- main action is readable at phone size
- text overlays are short, large, centered or top-aligned, and inside safe zones
- color contrast is strong enough for mobile feeds
- export dimensions match the target family
- final accepted files live under `assets/marketing/`

## Screenshots And Covers

- never accept a raw frame as the final marketing screenshot
- choose frames with motion, stakes, success, failure, enemies, rewards, or visible progress
- use one hook line, not a paragraph
- do not cover the main character, target, score moment, or reward
- cover images are for platform upload flows; thumbnails are separate exported files

## Videos

- action starts in the first 1 to 2 seconds
- captured game audio is preserved when available and licensed
- captions and overlays still communicate the hook while muted
- trim dead time before and after the strongest moment
- avoid rapid cuts that hide how the game is played

## Hero Art And Icon

- generate or edit base artwork with PlayDrop AI image generation
- validate artwork quality before compositing title typography
- composite the game title using a real project or licensed font
- reject AI-rendered title text when it is distorted or misspelled
- reject raw screenshots as icon or hero art
- hero art should feature the game name prominently and fit the shipped art direction
- icon art should read clearly at small sizes without depending on tiny text

## Rejection Conditions

- generic artwork that could fit any game
- misleading features or characters not present in the game
- low-resolution or blurry exports
- text clipped by the frame or unreadable on mobile
- missing audio when the declared policy requires audio
- outputs saved only under `output/` or temporary folders
