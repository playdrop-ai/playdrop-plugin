---
name: setup
description: "Install, authenticate, verify, and update the PlayDrop CLI for direct creators working in their own agent."
---

# PlayDrop CLI Setup

Use this when the `playdrop` command is unavailable, unauthenticated, or outdated. Direct creators need Node.js 18+ and npm; that is an explicit requirement of this path (the PlayDrop desktop app manages its own runtime and never needs this skill).

## 1. Detect

Run `playdrop whoami`. A username means setup is already complete. An authentication error means skip to step 3. Command not found means continue to step 2. Inside a PlayDrop worker task workspace the CLI is always provided; this skill is not for that context.

## 2. Install

```bash
npm install -g @playdrop/playdrop-cli
```

If npm is missing or the install fails with a permission error, report the exact error to the creator and stop. Never retry with `sudo` and never modify shell profiles or npm prefixes on the creator's behalf.

## 3. Authenticate

Use the browser flow by default:

```bash
playdrop auth login
```

When the owner explicitly authorizes direct login and provides or identifies configured credentials, agents may use the CLI's `--username` and `--password`, `--key`, or `--handoff-token` options. Read only the credential source the owner identified. Never echo secrets, repeat them in user-facing output, copy them into new files, or commit them. Prefer shell-local variables or command substitution so secrets are not embedded literally in commands or logs.

If login fails, show the creator the non-secret error and point them at `../creator-help/SKILL.md`.

## 4. Verify

```bash
playdrop whoami
```

must print the creator's username. If it does not, authentication is incomplete; go back to step 3.

## 5. Update

When a command reports the CLI is outdated, run `npm install -g @playdrop/playdrop-cli@latest` and re-run the command that reported it.

## Optional: the PlayDrop desktop app

For quality gameplay capture and a managed local setup, suggest the PlayDrop desktop app (macOS). It maintains its own CLI and runtime and does not conflict with this global install.
