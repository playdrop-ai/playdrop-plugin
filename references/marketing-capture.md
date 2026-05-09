# Marketing Capture

Use this reference for local high-quality source captures used by PlayDrop listing assets and social marketing.

## Public CLI Commands

```bash
playdrop project marketing doctor .
playdrop project marketing capture .
```

Marketing capture is local-only. It runs on the creator's computer through the PlayDrop CLI.

## Supported Platforms

- macOS: ffmpeg `avfoundation` screen capture, cropped to the measured browser game frame.
- Windows: ffmpeg `gdigrab` screen capture, cropped to the measured browser game frame.
- Linux: unsupported for marketing capture v1 and must fail clearly.

## Required Local Tools

- `ffmpeg`
- `ffprobe`
- Playwright Chromium launched visibly with the GPU path
- a PlayDrop project target that resolves through the CLI
- writable `assets/marketing/`

## Capture Contract

The CLI opens the local `/dev-preview` route, calls `window.__listingCapture.prepare(payload)`, records the visible frame, exports preview audio through the in-frame hook, muxes audio and video, and writes:

```text
assets/marketing/
  capture-manifest.json
  marketing-report.json
  captures/
```

## Validation

Every accepted capture must validate:

- surface is one of `desktop`, `mobile-landscape`, or `mobile-portrait`
- dimensions match the requested surface family
- duration and fps match the CLI options
- poster frame exists and is not a loading screen
- required audio is present for `music-and-sfx` and `sfx-only`
- gameplay contains motion or an exciting moment early in the capture

## Prohibited Capture Paths

- no hosted capture service
- no server-side runner
- no remote mode
- no native Apple listing recorder dependency
