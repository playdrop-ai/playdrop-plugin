# Performance Debugging

Use this when a Playdrop game has intermittent frame drops, browser-specific regressions, or unclear performance bottlenecks.

Start with:
- `playdrop project validate .`
- `playdrop detail playdrop/app/starter-kit-racing --json`
- `playdrop detail playdrop/app/starter-kit-3d-platformer --json`
- `playdrop detail playdrop/app/starter-kit-fps --json`
- `playdrop project capture` or `playdrop project capture remote` if hosted proof is needed

Default rule:
- optimize from a deterministic reproduction, not from anecdotal playtesting alone
- measure frame time spikes, not only average FPS
- add `window.advanceTime(ms)` and `window.render_game_to_text()` early
- create short scripted or ghost-run scenarios for idle, stress, and action-heavy cases
- profile both the raw harness surface and the real hosted `/play` route
- compare the same scenario in Chrome and Safari or WebKit before guessing at root cause

Instrumentation checklist:
- record average frame time, p95 frame time, worst frame, and counts above frame-time thresholds
- record draw calls and triangles once per frame, not by monkey-patching WebGL calls
- attach a small ring buffer of recent events to slow frames, for example jump, shoot, hit, coin, land, break, fall, and audio events
- add subsystem timing only where needed, such as physics, render, AI, triggers, effects, and audio
- reset perf samples after loading so startup work is not misdiagnosed as gameplay stalls

Good workflow:
- freeze one exact benchmark route per game and per stress case
- use the same viewport and scenario across browsers
- run Chrome and WebKit side by side on the same `test-host.html?benchmark=1&ghostRun=...`
- if the problem is Safari-only, isolate shared suspects one at a time such as audio, debug DOM updates, shadows, clouds, or postprocessing
- if one subsystem toggle collapses the spikes, treat that as the lead and fix the architecture instead of adding blind quality cuts
- confirm the fix with the same benchmark route and the same instrumentation output

Chrome and Safari split:
- Chrome is a useful control because it often shows whether the game is fundamentally heavy or whether the issue is browser-specific
- WebKit or Safari should be treated as the source of truth for Safari regressions
- headless browser numbers are good for controlled comparison, but they are not a substitute for real hosted validation on the actual Playdrop route

When Safari is the problem:
- prefer real Safari or Playwright WebKit reproduction first
- if possible, capture Safari Web Inspector timelines or macOS process traces after the deterministic reproduction is in place
- if the hitch happens on specific gameplay actions, instrument the action path directly before touching renderer settings
- test audio separately because Safari-specific audio spikes can look like random rendering stalls

Classify the issue:
- steady low FPS usually means constant GPU or CPU cost
- occasional huge frame spikes usually mean sporadic work such as allocation, decode, DOM churn, audio resume, or expensive trigger paths
- startup spikes should be tracked separately from live gameplay spikes

Suggested result:
- every Playdrop game should have one deterministic stress route, one text snapshot hook, and one lightweight slow-frame log so cross-browser debugging stays fast and evidence-driven
