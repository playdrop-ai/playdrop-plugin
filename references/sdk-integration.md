# SDK Integration

Use this reference when the work depends on the public Playdrop SDK lifecycle instead of only CLI setup.

## Core flow

1. initialize the SDK first
2. wait for the runtime context before reading player or game state
3. keep integration scope small and add only the features the project actually needs
4. re-test the same integration through the local dev flow after every meaningful change

## Common integration surfaces

- player identity and profile surfaces
- game state and metadata access
- saves and cloud-backed progress
- realtime messaging and multiplayer state
- monetization or rewarded flows when supported by the current public docs

## Rules

- prefer the live public docs when behavior may have changed
- update only the SDK and project surfaces that matter for the requested change
- pair SDK changes with validation, not just code edits
