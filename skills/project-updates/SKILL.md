---
name: project-updates
description: "Update Playdrop CLI, plugin, SDK, and project compatibility. Use when the user asks to upgrade Playdrop tooling, compare versions, read changelogs, or migrate an existing project to current public best practices."
---

# Project Updates

Use this skill when the request is about staying current rather than building a new feature.

## Workflow

1. Check installed CLI version with `playdrop --version`
2. Read relevant live docs or changelog entries
3. Update only the surfaces that matter
4. Validate with `playdrop project validate .`
5. Re-test on the dev flow before publish

## Shared references

- `migration-guide.md`
- `cli-map.md`
- `services.md`
- `sdk-integration.md`
- `platform-capabilities.md`

## Handoff

- runtime feature work after an upgrade -> `service-integration`
- multiplayer or auth-sensitive validation -> `dev-testing`
