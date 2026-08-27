# Generated Assets

Use this when catalogue packs and individual assets cannot cover an asset need (identity, unique props, themed tiles). Derive everything from the approved hero art and art-direction board. Generation follows the `skills/make-assets` preference order.

Generate needed images individually with native tooling when possible. Condition them on the strongest approved identity reference when helpful. If generation returns a sheet, use `skills/make-2d-asset-pack` to split it and remove the matte; never use the source sheet directly. Save each accepted transparent PNG under `assets/generated/<asset-name>.png`. Use isolated centered assets with complete silhouettes, no text, no frame, and consistent lighting. Keep the set small and coherent: a few assets that match beat many that don't.

Every generated gameplay file must be declared in `ownedAssets`, loaded by the runtime, and visibly rendered in playtest. Hosted workers should report useful accepted assets when the material protocol is available, but reporting is best-effort and must never block delivery. A file that is not packaged and visibly rendered does not exist.

Background parallax layers are full-canvas alpha layers, never sprite-style cutouts. For coherent families with more than about six independent assets or for multi-family packs, prefer the `make-2d-asset-pack` skill as its own job over hand-rolling inside a build.
