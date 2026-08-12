---
name: market-game
description: "Create or update a PlayDrop game marketing package. Use when the user asks to create the marketing package, market a game, generate store and social assets, or refresh existing game marketing. Coordinates a short marketing brief, a marketing-ready preview, truthful videos, promotional images, listing metadata, social mappings, catalogue updates, and private draft delivery through the existing specialist skills."
---

# Market Game

Use this after the game is playable. This skill defines the marketing package and routes production to the existing specialist skills.

## Scope

- If the package is empty, create the complete package below.
- If a package already exists, inspect it first and preserve approved work. Create or change only what is missing, failing review, or requested by the user.
- If the user requests one asset type or one correction, work only on that scope.

Never regenerate unrelated approved media merely to make an update look fresh.

## Marketing package

1. Create a short brief at `assets/marketing/playdrop/marketing-brief.md` with:
   - the strongest truthful player promise;
   - the key gameplay moments to showcase;
   - four distinct selling points with short headlines;
   - the game evidence supporting each claim.
2. Inspect the normal game preview. Improve it only when needed so it is a HUD-free, marketing-worthy demonstration of the real game that teaches the input, escalates, and reaches a real payoff. Use `make-listing` for the preview and capture contract.
3. Use `make-marketing-video` to produce:
   - one 16:9 PlayDrop store video;
   - one 16:9 YouTube and X trailer;
   - one 9:16 short for YouTube Shorts, TikTok, and Instagram;
   - one 9:16 PlayDrop preview when the game supports portrait play.
4. Use `make-marketing-screenshots` to produce:
   - four 16:9 PlayDrop store images;
   - four 9:16 Instagram images;
   - the same four ordered selling points in both orientations, composed natively for each ratio.
5. Update the description and tags when needed to match the approved promise and shipped game.
6. Use `make-social-media-package` to map the approved videos and portrait images to YouTube, TikTok, Instagram, and X without duplicating identical files.
7. Use `make-listing` to wire the approved media and metadata into `catalogue.json`.

Reuse one approved canonical video for multiple destinations when its ratio, framing, pacing, safe areas, and truthfulness already fit them. Do not create duplicate physical files only to satisfy multiple mappings.

## Production rules

- Gameplay video is real captured gameplay. Marketing images and video selling-point graphics may be AI generated, but must advertise only shipped content.
- Treat `previewable: true` as a capability flag, not proof that the preview is good marketing footage.
- Preserve the title, subtitle, icon, and hero images unless they are inaccurate or the user requested changes.
- A raw recorder take is source footage, not a finished trailer.
- A required missing or failed video is a hard failure. Do not replace it with `null`, `pending`, a note, or a partial package upload.
- Validate the game after the last preview change, then complete each specialist skill's media review.

## Studio delivery

For a PlayDrop Studio agent task, upload one complete `PRIVATE` patch update after self-review. Do not publish it and do not pause for intermediate approval. The private draft is where the creator reviews the result.

Outside Studio, follow the delivery scope of the invoking workflow.

## Not building

- No new gameplay features beyond truthful preview and capture support.
- No unsupported claims or generated gameplay footage.
- No automatic publication or social posting.
- No unrelated asset regeneration during a narrow update.
