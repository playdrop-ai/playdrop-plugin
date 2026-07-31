# Update Game Phases

An update is not a miniature new-game build. Choose only phases that describe actual work, and skip, reorder, or re-enter them as needed.

- `setup` or `understand`: review the request, current game, and behavior that must keep working.
- `research`: use only when the request requires outside reference or catalogue research.
- `debugging`: use when reproducing a bug, tracing a failure, or finding a root cause.
- `designing`: use when defining a new mechanic, feature, flow, or meaningful rules change.
- `drawing`: use when changing the art direction or creating new visual assets.
- `prototyping`: use when a risky new interaction needs a rough playable proof.
- `tweaking`: use for focused tuning, balance, copy, layout, animation, or polish changes.
- `coding`: use for implementation work that is broader than a focused tweak.
- `playtesting`: validate the requested behavior and the existing core loop on the primary surface with evidence per `skills/playtest-game/SKILL.md`.
- `recording`: use only when the request changes listing media or needs a refreshed recording. In a task, share one representative primary-surface source still as `--title "Real Game"` and one primary-surface video with its poster as `--title "Game Recording"`. These are gameplay evidence and image-generation references, not final listing screenshots. Final listing screenshots use the separate fully AI-generated marketing workflow. Never share a composite board or secondary-orientation media as gameplay evidence. Windows Local Agent and direct-creator tasks do not produce video materials unless a supported external capture workflow is available.
- `finalizing`: complete preflight, upload, and creator handoff.

Typical examples are Reviewing, Debugging, Coding or Tweaking, Playtesting, Finalizing for a bug; or Reviewing, Designing, Drawing or Crafting, Coding, Playtesting, Recording, Finalizing for a visual feature. They are suggestions, not scripts.

Update only the optional primary tag refs in `catalogue.json.design` that changed. Preserve useful project prose rather than replacing it. If the change alters the fantasy, surface, or visual promise, refresh the affected art-direction artifacts before producing new assets. Art-chain contracts apply to what you touch; they are not a migration mandate for untouched parts of older games.

Do not bury a broken core loop under visual polish. If the existing game is too broken for the requested update, say so and fail or propose a smaller first fix.
