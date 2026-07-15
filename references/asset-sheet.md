# Generated Assets

Use this when catalogue packs and individual assets cannot cover an asset need (mascot, unique props, themed tiles). Derive everything from the approved hero art and art-direction board. Generation follows the `skills/make-assets` preference order.

Generate needed images individually with native tooling, each conditioned on `assets/art-direction/hero-portrait.png` (and the board when helpful) for style consistency. Save each PNG under `assets/generated/<asset-name>.png`. Use isolated centered assets with complete silhouettes, transparent or easily removable flat backgrounds, no text, no frame, and consistent lighting. Keep the set small and coherent: a few assets that match beat many that don't.

Background parallax layers are full-canvas alpha layers per `references/art-direction-board.md` step 5, never sprite-style cutouts.
