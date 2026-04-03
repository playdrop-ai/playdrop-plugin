# Audio

Use this when adding gameplay audio, debugging frame drops around sound-heavy actions, or choosing between audio APIs.

Start with:
- `playdrop detail playdrop/app/starter-kit-fps --json`
- `playdrop detail playdrop/app/starter-kit-3d-platformer --json`
- `playdrop search sound --kind asset --json`
- `playdrop search music --kind asset --json`

Default rule:
- use Web Audio for gameplay SFX and gameplay loops such as jump, shoot, hit, pickup, footstep, and break
- preload and decode gameplay sounds during loading instead of allocating or decoding on the action frame
- unlock the `AudioContext` on the first user gesture, ideally `pointerdown` or touch start, before gameplay begins
- keep `HTMLAudioElement` for simple music playback, previews, or non-critical UI use only
- do not use `HTMLAudioElement` hot paths for gameplay one-shots with `pause()`, `currentTime = 0`, `playbackRate` changes, and `play()` inside the main action loop
- if Safari or iPhone Safari drops frames on jump, shoot, collect, or land while Chrome is fine, suspect audio early

Critical checks:
- audio preload finishes before the player can enter gameplay
- gameplay one-shots use `AudioBufferSourceNode` and short-lived gain nodes instead of recycled DOM audio tags
- continuous loops such as footsteps use Web Audio loop sources or a stable loop state instead of repeated restarts
- the first audio unlock cost does not land on the same frame as the first visible gameplay transition if you can avoid it
- music and gameplay SFX use different policies so a simple music need does not force a bad gameplay SFX architecture

Good workflow:
- separate music, UI audio, and gameplay SFX first
- preload only the gameplay SFX needed for the opening play session
- log audio events with timing while profiling so slow frames can be matched to recent sound activity
- if Safari hitches but Chrome does not, temporarily stub audio to confirm or rule it out quickly
- once the cause is confirmed, replace the hot path instead of adding browser-specific fallbacks

Compare:
- Chrome versus Safari or WebKit on the same scripted run
- gameplay with real audio versus a silent audio stub during local diagnosis
- average update time before and after the audio change
- slow-frame event logs before and after the audio change

Safari notes:
- Safari can tolerate background music but still hitch badly on gameplay SFX if they are driven through `HTMLAudioElement` in hot paths
- recurring hitches on jump, shoot, collect, and footstep loops are often audio architecture problems, not rendering problems
- a one-time `AudioContext.resume()` bump is very different from recurring gameplay spikes, so classify them separately

Suggested result:
- use a small shared Web Audio bus for gameplay SFX and loops, preload it during loading, and keep the diagnostic path simple enough that audio can be isolated quickly when browser-specific spikes appear
