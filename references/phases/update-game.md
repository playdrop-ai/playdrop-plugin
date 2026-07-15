# Update Game Phases

1. `setup`: validate the staged project, confirm app name/version, and inspect `catalogue.json`.
2. `understand`: inspect the current game and identify what must keep working.
3. `plan`: scope the change and update only the optional primary tag refs in `catalogue.json.design` that changed. Preserve and update useful project prose rather than replacing it. If the change alters the fantasy, surface, or visual promise, refresh the affected art-direction artifacts (art concept, heroes, board) before producing any new asset.
4. `implement`: change only what the request needs. Art-chain contracts (backgrounds, boards, heroes) apply to what you touch; they are not a migration mandate for untouched parts of older games.
5. `playtest`: run `playdrop project check .` with focused-frame actions that exercise current behavior plus the new behavior on the primary surface, with evidence per `skills/playtest-game/SKILL.md`.
6. `listing-refresh`: update listing assets only when the experience or promise changed.
7. `wrap-up`: validate, upload/publish as instructed, and suggest next steps.

Do not bury a broken core loop under visual polish. If the existing game is too broken for the requested update, say so and fail or propose a smaller first fix.
