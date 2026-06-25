# Performance / Stability

This dimension is about whether the game behaves like a credible product during real play. A game can have a promising loop and still fail distribution quality because it loads too slowly, stutters too much, crashes, leaks state, or degrades under normal interaction. Review this as a player-facing reliability question, not only a technical question.

## Comparison discipline

Compare against games with similar technical demands and pacing.

- a simple 2D arcade game is expected to feel very stable and fast
- a heavier 3D game may tolerate more load time, but not severe frame instability
- latency sensitivity depends on genre, but action, platforming, and rhythm-like timing need a stricter bar

Ask whether the performance is merely unoptimized, or whether it materially harms the intended player experience compared with real peers.

## What to inspect

- load time
- frame pacing
- input responsiveness under load
- session stability
- restart and retry stability
- obvious console-breaking errors when they affect runtime quality

## Evidence to gather

- run a real session from startup to several minutes of play
- trigger restarts, transitions, menus, and repeated interactions
- note if degradation builds over time
- observe whether bugs are cosmetic, disruptive, or session-ending

## Questions to answer

- Can the player start playing quickly enough for the genre?
- Does the game remain stable through ordinary use?
- Is frame rate good enough that the controls and readability still make sense?
- Are there bugs severe enough to undermine the submission's quality judgment?
- Is any technical issue likely to dominate the player's impression?

## Common failure modes

- long blank or confusing startup before the first playable moment
- severe frame drops when the core loop becomes interesting
- state corruption after restart or relaunch
- crashes or softlocks during common flows
- browser or runtime errors that visibly break UI, audio, saving, or progression

## Stage-aware interpretation

At prototype stage, some rough edges are expected. Repeated instability that prevents fair evaluation is not. By `Demo`, the game should survive a normal session. By `First Release`, stability and acceptable performance are part of the bar for being publicly distributed without limitation.

## What strong feedback looks like

- "The game is technically playable, but the frame drops arrive exactly when enemy count increases, which means the core appeal is being tested under its weakest performance conditions."
- "Load time is longer than ideal, but the bigger issue is that the player gets no clear progress signal during startup, making the wait feel even worse than it is."
