# Generated Assets

Use this when catalogue packs and individual assets cannot cover an asset need (identity, unique props, themed tiles). Derive everything from the approved hero art and art-direction board. Generation follows the `skills/make-assets` preference order.

Generate needed images individually with native tooling, each conditioned on `assets/art-direction/hero-portrait.png` (and the board when helpful) for style consistency. Save each PNG under `assets/generated/<asset-name>.png`. Use isolated centered assets with complete silhouettes, transparent or easily removable flat backgrounds, no text, no frame, and consistent lighting. Keep the set small and coherent: a few assets that match beat many that don't.

Every generated gameplay file must be declared in `ownedAssets`, loaded by the runtime, and visibly rendered in playtest. A file that is not packaged and rendered does not exist.

Background parallax layers are full-canvas alpha layers per `references/art-direction-board.md` step 5, never sprite-style cutouts. For large coherent families (more than ~6 items, paired size variants, multi-family packs), prefer the `make-2d-asset-pack` skill as its own job over hand-rolling inside a build.
