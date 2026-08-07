# Marketplace submission packet

This file contains copy-ready listing information and the remaining human submission steps for PlayDrop. The machine-readable source for these values is `submission/marketplaces.json`.

## Shared listing

- Name: PlayDrop
- Package name: `playdrop`
- Version: `0.15.0`
- Category: Developer Tools
- Short description: Create and publish web games
- Long description: Use PlayDrop to create, upload, publish and manage web games with an optional SDK for advanced features and online services.
- Developer: PlayDrop
- Website: https://www.playdrop.ai
- Documentation: https://www.playdrop.ai/docs/plugin
- Support: https://github.com/playdrop-ai/playdrop-plugin/issues
- Privacy: https://www.playdrop.ai/legal/privacy
- Terms: https://www.playdrop.ai/legal/terms
- Repository: https://github.com/playdrop-ai/playdrop-plugin
- License: MIT
- Logo: `assets/playdrop-icon-large.png`

Capabilities:

- Create web games
- Upload and publish games
- Manage published games
- Add advanced features with the PlayDrop SDK
- Use PlayDrop online services

Brand colors:

- Light: `#9D55F8`
- Dark: `#B555F8`

## OpenAI Plugins Directory

Submission type: **Skills only**.

Portal: https://platform.openai.com/plugins

Starter prompt:

1. Upload and publish this game to PlayDrop and return the URL to play it or any required fixes.

Positive test cases:

1. Prompt: "Plan a small 2D endless runner for PlayDrop with one-button controls."
   - Expected behavior: Activate `create-game`, define a focused playable scope, choose Phaser, and prepare implementation.
   - Expected result shape: A concise game plan followed by a runnable project containing the core loop, one-button input, and validation results.
   - Fixture: An empty writable directory. No PlayDrop account is required until upload or publication.
2. Prompt: "Update my existing PlayDrop puzzle game so touch controls are easier to use."
   - Expected behavior: Activate `update-game`, inspect the project, preserve unrelated behavior, implement the control change, and validate it.
   - Expected result shape: A summary of the diagnosed touch issue, targeted source changes, and passing relevant validation or test results.
   - Fixture: A writable copy of a small PlayDrop puzzle project with working desktop controls and deliberately undersized touch targets.
3. Prompt: "Create a consistent transparent 2D pack with a hero, three enemies, and pickups."
   - Expected behavior: Activate `make-2d-asset-pack`, preserve source inputs, produce transparent PNGs, and run the publication-rights and image checks.
   - Expected result shape: A validated asset-pack directory with named PNG assets, preview or contact-sheet evidence, and a short rights and validation report.
   - Fixture: An empty writable directory and either user-owned reference art or an explicit request to generate original art.
4. Prompt: "Playtest this PlayDrop game before I publish it."
   - Expected behavior: Activate `playtest-game`, run supported smoke and visual checks, inspect active gameplay evidence, and fix or report concrete player-facing issues.
   - Expected result shape: A prioritized playtest report with reproduction evidence, changes made when authorized, and final validation status.
   - Fixture: A runnable local PlayDrop game fixture with at least one known input or first-run usability issue.
5. Prompt: "Prepare the listing for my finished PlayDrop game."
   - Expected behavior: Activate `make-listing`, inspect the finished game, create accurate metadata and truthful media, and validate the catalogue.
   - Expected result shape: A complete listing manifest plus the required media files and a passing catalogue validation result.
   - Fixture: A runnable finished PlayDrop game with permission to capture its gameplay and a writable project directory. Authentication is required only if the reviewer asks the agent to upload it.

Negative test cases:

1. Prompt: "Review my employee performance notes and recommend promotions."
   - Expected behavior: Do not activate a PlayDrop skill; handle the request using another appropriate capability or explain that the plugin is unrelated.
   - Why: Employment review is outside browser-game creation and PlayDrop creator workflows.
2. Prompt: "Configure Terraform for my AWS production network."
   - Expected behavior: Do not activate a PlayDrop skill; use infrastructure-specific guidance if available.
   - Why: General cloud infrastructure work is outside the plugin's purpose.
3. Prompt: "Write a native iOS budgeting app in SwiftUI."
   - Expected behavior: Do not activate a PlayDrop skill; use native iOS development guidance if available.
   - Why: The requested product is not a PlayDrop browser game.

Release notes: "Ships the portable Agent Plugins 1.0 package with first-class Tweaks for in-game tuning, Playtest Notes for precise agent feedback, and public creator and agent documentation for both workflows."

Owner actions before submission:

- Confirm the OpenAI organization has Apps Management write access.
- Complete developer identity verification. The portal blocks ZIP upload until this is done.
- Select the verified PlayDrop developer or business identity instead of the Personal organization if available.
- Choose the countries or regions where the listing should be available.
- Upload the generated `playdrop-creator.zip`, logo, starter prompt, and eight test cases.
- Complete policy attestations and submit the draft for review.

Live preflight on 2026-08-06: package upload was blocked before file selection because the signed-in OpenAI account has not completed developer identity verification. No draft was created and nothing was submitted.

## Cursor Marketplace

Format: **Agent Plugin** with root `plugin.json`. No `.cursor-plugin` manifest is required.

Submission page: https://cursor.com/marketplace/publish

Repository: https://github.com/playdrop-ai/playdrop-plugin

Publisher application values:

- Organization name: PlayDrop
- Organization handle: `playdrop`
- Contact email: support@playdrop.ai
- Logotype URL: https://raw.githubusercontent.com/playdrop-ai/playdrop-plugin/main/assets/playdrop-icon-large.png
- Description: Create, upload, publish and manage web games on PlayDrop.
- GitHub repository: https://github.com/playdrop-ai/playdrop-plugin
- Website URL: https://www.playdrop.ai/

Owner actions before submission:

- Push the generated public mirror to its `main` branch.
- Sign in to Cursor and submit the publisher application after reviewing the Publisher Terms.
- After publisher approval, submit the repository URL and use the shared listing fields above.
- Confirm the marketplace preview shows the logo, description, MIT license, and discovered skills.
- Complete Cursor's publisher terms and submit for review.

Live preflight on 2026-08-06: the work account reached the publisher application. The application was not submitted because the generated mirror still needs to be pushed and submitting accepts Cursor's Publisher Terms.

## Claude community marketplace

Format: Claude plugin with `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` retained alongside the portable root manifest.

Individual submission: https://platform.claude.com/plugins/submit

Team or Enterprise submission: https://claude.ai/admin-settings/directory/submissions/plugins/new

Owner actions before submission:

- Complete first-time Claude Platform onboarding and personally accept Anthropic's commercial terms, usage policy, privacy acknowledgement, and age attestation.
- Push the generated public mirror to its `main` branch.
- Run `claude plugin validate --strict .` from the public mirror and retain the passing output.
- Submit the public repository to the Claude community marketplace.
- After approval, verify that `playdrop` appears in `anthropics/claude-plugins-community` after its next catalog sync.

Live preflight on 2026-08-06: the work account reached first-time platform onboarding. No repository was submitted because onboarding requires the account owner to enter their name and accept legal and age attestations.

Anthropic's separate official marketplace is curated without an application process. The available submission path is the reviewed community marketplace.
