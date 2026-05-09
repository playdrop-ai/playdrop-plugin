# Marketing Audio

Use this reference when preparing preview scenes, marketing captures, videos, and `MARKETING.md` audio notes.

## Audio Policies

`catalogue.json` must declare one preview audio policy:

- `music-and-sfx`: preview includes background music and gameplay sound effects.
- `sfx-only`: preview includes gameplay sound effects but no background music.
- `silent`: preview intentionally has no audio.

`silent` is allowed only when silence is a deliberate game-design choice. Explain the reason in `MARKETING.md`.

## Requirements

- `music-and-sfx` and `sfx-only` require the preview audio hook to export audio for marketing capture.
- Capture validation must fail clearly when required audio is absent.
- Capture validation must fail when non-silent audio is present but too quiet for marketing use.
- Social videos still need readable text overlays because many platforms autoplay muted.
- Use game audio, PlayDrop catalogue songs and SFX, or PlayDrop AI-generated music and SFX.
- Do not add unlicensed music, trending platform audio, or commercial tracks outside the creator's rights.
- Default marketing packs should use `music-and-sfx`. Add background music through PlayDrop catalogue audio or PlayDrop AI generation when the game has no suitable music.
- `sfx-only` is an exception for games that intentionally have no music. Document the reason in `MARKETING.md`.
- Final social videos should normalize captured game audio for social playback. A good target is roughly `-16 LUFS` integrated with peaks below clipping.

## MARKETING.md Notes

Document:

- declared preview audio policy
- music and SFX source names
- whether PlayDrop AI generation was used
- intentionally silent outputs and reasons
- any platform upload notes about muted autoplay
