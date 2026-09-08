---
name: localize-game
description: "Localize an existing PlayDrop game's interface, catalogue listing, and requested listing images. Use for adding languages or auditing localization coverage, including listing-only work for externally hosted games."
---

# Localize Game

Follow `../update-game/SKILL.md` for runtime updates and `../make-listing/SKILL.md` for listing work. Apply the creator's requested languages and scope; do not treat localization as permission to change platform code, accounts, external deployments, or publish.

## Find the actual gaps

Compare the local catalogue with the live listing before producing translations, and carry forward correct live translations that are missing locally. Available listing locales prove only that translated catalogue content exists; they do not prove that the runtime, images, or videos are localized. Preserve correct existing translations and media. Compare live media slots, including social share cards, against local declarations: version-scoped assets missing from the next upload can disappear even when the local catalogue never declared them. Carry forward still-useful live assets and include them when recomputing the source hash.

Distinguish game-owned UI, PlayDrop-hosted UI, and text embedded in images/video. For EXTERNAL games, update only the managed listing unless the creator has authorized changes to the external source and deployment. Report the scope accurately. Verify the external game's existing language support before making claims about it; listing-only work does not imply an English-only runtime. Describe the language visible in reused footage separately from the current game's supported languages.

## Language and title choices

- Preserve the creator's established brand and approved localized titles. Keeping an English brand in Latin-script markets, transliterating it for Japanese/Korean, and adapting it for Chinese are useful starting points, not mandatory regional rules. Descriptive titles may benefit from translation in any market.
- Use one approved display title consistently across listing, game, and localized hero images. Preserve slug, creator, save keys, item IDs, and achievement IDs.
- Translate dynamic feedback, results, tutorials, character/world names, and accessibility labels as well as menus. Keep a small shared dictionary with matching keys and interpolation parameters. Format visible numbers with the selected locale.
- Read the current SDK locale contract. Initialize game text from the host locale before building the first UI; verify page language, supplied SDK locale, and visible game text separately. A translated listing cannot prove that the host sends the right locale.
- Fit real text on supported surfaces, especially long French/German labels and CJK fonts. Prefer concise natural copy to shrinking everything. Separate missing host-owned translations from game defects; inspect current achievement/leaderboard localization support rather than assuming it exists or remains absent.

## Pragmatic media default

**Keep the original-language trailer and add an English version only when the original differs and an English version is needed. Do not generate one trailer per listing language by default.** A text-free trailer can serve both purposes as one file. Preserve existing useful localized trailers; this default does not request their deletion.

Reuse the selected video paths across localized listing snapshots and translate their title, caption, and description. Be honest about the language heard or visible in the footage. Reuse original footage when it still accurately depicts the shipped game; avoid implying that an external game's UI is translated. Add other trailer languages only when the creator requests them or approves a concrete audience need. Do not add video to a text-only task.

For requested images, localize visible copy and approved titles, including number formatting. Reuse text-free icons and unchanged-title heroes. Follow `../make-marketing-screenshots/SKILL.md` and the identity rules in `../make-listing/SKILL.md`; preserve actual game content and avoid unnecessary redesign. Use the original artwork as the edit source; accepted translated images can serve as style references, so visual changes do not accumulate across locales.

When new video is needed, use `../make-marketing-video/SKILL.md`. Prefer 30 fps capture and delivery for this localization workflow unless the creator or footage requires otherwise. Check real-time motion, audio, and representative frames. Use a representative image/video pilot before expanding the batch; bound concurrent generation and capture to available machine resources. Match returned images to their visible content and prompt identity, not completion order.

## Catalogue and delivery

- Use the installed CLI's current catalogue schema. Set `sourceLocale` and complete `listingLocalizations` snapshots with translated display name, subtitle, description, populated controls/making-of, release notes, and screenshot/video metadata. Preserve media slugs and existing supported surfaces. Localizations are complete snapshots: explicitly declare reused media, including social cards, in every applicable locale. Upload byte deduplication does not make omitted fields inherit from the source listing.
- Compute each translation's `sourceHash` from the final source listing and source media using the CLI's canonical hash implementation. Changes to source release notes also change that hash. Never substitute the runtime bundle hash or carry a stale hash forward after edits.
- Validate actual exported dimensions, file types, byte sizes, and the total upload before producing the whole asset batch. Use current service/CLI limits; account storage entitlement and per-file/per-upload caps are separate constraints. Accept exports that already pass the actual geometry and byte limits; do not invent a lower preferred size or repeatedly optimize valid files. Correct small dimension mismatches with deterministic resizing; regenerate for visible content defects. Keep raw masters and duplicate marketing trees out of the runtime/source archive, while retaining catalogue-declared delivery files.
- Finish runtime edits before new captures, record the tested build hash, and verify representative images at full and thumbnail size. Check number grouping and decimal punctuation in enlarged crops when thumbnails make them ambiguous. Do not repeatedly regenerate accepted art for marginal polish; record creator-approved exceptions accurately.
- Run package checks and the required final gameplay tapes after the final runtime change. Count package tests already invoked by CLI validation toward these checks; repeat them only after a change, failure, or unresolved concern. Inspect evidence for successful play, not merely input delivery. Check localized results/retry and preview-to-play transitions; test text layout across requested languages and supported surfaces without claiming simulated result screens prove natural gameplay success.
- If startup regresses, trace it before optimizing. Readiness follows a real frame. For Three.js, async compilation must cover actual scene/post-processing variants; inspect the loaded engine version before changing shadow modes or other render settings. Do not reduce visual quality to conceal a stall.
- Publish only within the creator's authorized workflow. Verify the live version, selected listing locale, representative localized media, and hosted runtime against the tested build. Report runtime, catalogue, assets, and remaining host limitations separately.

## Improve this workflow

After a concrete failure or useful simplification, update the relevant instruction in this skill or its owning specialist skill. Keep historical logs and game-specific measurements in the game project. Verify current contracts before turning an old platform bug or limit into a permanent rule. Prefer a short correction over accumulating checklists, copied schemas, or release-specific workarounds.
