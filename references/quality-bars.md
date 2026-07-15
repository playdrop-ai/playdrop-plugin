# Builder V2 Quality Bars

- Fullscreen gameplay first. The play canvas fills the entire surface: no letterbox bars, no dead zones, no page scroll, no card framing, no large title/stats/controls zones.
- No in-game title on the play surface unless it is part of a short preview/menu state.
- HUD is a minimal overlay rendered on top of gameplay: icons and numbers only, no text labels, no instructional sentences parked on screen.
- Dialogs and overlays (win, loss, pause) are centered on the play canvas.
- Optimize for the creator surface by default. Escape only when the requested game is a terrible fit for that surface.
- Primary entities must be visible, correctly scaled, and stylistically coherent.
- A simple coherent asset set beats a large mismatched one.
- Core actions need immediate feedback: movement, hit, collect, build, upgrade, wave clear, win, loss, and restart.
- The first playable frame must show real gameplay objects, not blank space, loading leftovers, or only a menu.
- The loop needs stakes: timer, enemies, resource pressure, puzzle constraint, score target, risk, or mastery.
- The game must be previewable when marked previewable.
- Listing hero art must depict the real game fantasy and core entities. It can be aspirational, not dishonest.
- Scope cuts should become next-step suggestions, not hidden omissions.
- If something required fails validation or cannot be made honest, stop and fail clearly.
