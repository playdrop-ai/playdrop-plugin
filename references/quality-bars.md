# Builder V2 Quality Bars

Outcome bars: each says what must be true on screen, never how to build it. Engine mechanics live in `references/tech/`; art mechanics in `references/art-direction-board.md`.

- Fullscreen gameplay first: the play canvas fills the entire surface. No letterbox bars, dead zones, page scroll, or card framing; filled by scaling that never stretches or distorts.
- Controls and overlays stay aligned with gameplay at every scale and read as one coherent designed surface with the canvas (engine mechanics and known failure modes: `references/tech/`).
- No in-game title parked on the play surface outside a short preview/menu state.
- HUD is minimal, safe-area aware, and instantly readable: status as icons and numbers, short labels only where an icon would be ambiguous, no instructional sentences parked on screen.
- UI reads as deliberately designed and coherent with the art direction: buttons, dialogs, and meters in the direction's material language, never default engine placeholders. Technique is yours: image chrome, vector, or engine-drawn all qualify.
- Dialogs and overlays center within the safe area of the play canvas.
- Primary entities are visible, correctly scaled, stylistically coherent, and real assets.
- Entities visibly belong to their background: sitting on its structures, matching its light.
- A simple coherent asset set beats a large mismatched one.
- Core actions give immediate feedback: movement, hit, collect, win, loss, restart.
- The first frame is a designed screen of the game (the board's title or gameplay screen, real art), never blank space, loading leftovers, default engine chrome, or an offscale canvas; core gameplay is reachable within one input.
- The loop has designed pressure fitting its declared progression: stakes, timer, difficulty, or mastery. Endless loops still need tension or failure, and restart.
- The game must be previewable when marked previewable.
- Listing art depicts the real game fantasy and core entities: aspirational is fine, dishonest is not.
- Scope cuts become next-step suggestions, not hidden omissions.
- If something required fails validation or cannot be made honest, stop and fail clearly. Media failure policy: `skills/make-assets`.
