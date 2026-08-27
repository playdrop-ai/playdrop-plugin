# Art Direction

Use art-direction artifacts when they reduce ambiguity or improve consistency. They are tools, not an ordered workflow or upload checklist. The agent may prototype first, explore art first, develop art and code together, or skip internal artifacts that would add no value.

Useful options:

- Art concept: fantasy, identity, setting, palette, and UI material language.
- Hero exploration: key art that establishes identity and can guide later images.
- Standalone gameplay mockup: one honest full-screen composition in the primary surface.
- Multi-screen board: useful for UI-heavy games or flows with several distinct states.
- Isolated assets and backgrounds: produce only what the runtime needs.

Share an approved artifact when it helps the creator follow progress. Do not create one merely to fill a conversation slot.

## Consistency

Choose the strongest approved visual as the identity reference and condition later generations on it when that improves consistency. `assets/art-direction/hero-portrait.png`, `hero-landscape.png`, `board.png`, and `mockup-gameplay-primary.png` are suggested paths when those artifacts exist, not required files.

Keep the identity subject, palette, lighting, and UI materials coherent. Real gameplay may improve on an early mockup, but it should still feel like the same game.

## Artifact standards

Hero art should sell the real game fantasy at an exciting moment, keep the exact game name legible near the center, and contain no unrelated UI, device frame, or watermark. Listing heroes remain subject to the listing contract even when no earlier exploration hero exists.

A gameplay mockup should show one undistorted, full-bleed primary-surface gameplay screen that the scoped build can honestly deliver. Do not share composite boards as gameplay mockups.

A board is useful only when several screens or states need coordination. Keep its frames in the primary orientation and limit it to screens the scoped game will actually ship.

For 2D games, use a background image when it improves the result. Fixed, tiled, parallax, procedural, or deliberately minimal treatments are all valid when they suit the game. Check coverage, seams, readability, and lighting during playtest.

## Generation

Follow `skills/make-assets` for sourcing and generation. Prefer reference conditioning for related images and inspect every accepted result. If an optional art-direction artifact fails, continue without it. Required listing identity follows `skills/make-listing`; gameplay-required media follows the clear-failure policy.
