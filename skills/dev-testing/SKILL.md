---
name: dev-testing
description: "Run Playdrop local development and validation workflows. Use when the user needs the dev server, local validation, test accounts, multiplayer checks, or staged creator testing before publish."
---

# Dev Testing

Use this skill to validate creator projects before they become listing or release work.

## Workflow

1. Log in and initialize the project if needed
2. Run `playdrop project validate .`
3. Start the local dev flow
4. Use multiple accounts when auth or multiplayer matters
5. Confirm the core runtime behavior before publish

## Rule

Keep this skill focused on correctness, setup, and validation. If the question is whether the game feels worth shipping, hand off to `gameplay-review`.

## Shared references

- `test-accounts.md`
- `performance-debugging.md`
- `sdk-integration.md`

## Handoff

- hook, feel, or session-quality review -> `gameplay-review`
- shipped listing and media -> `store-listing`
- runtime quality or polish work -> `game-improvement`
