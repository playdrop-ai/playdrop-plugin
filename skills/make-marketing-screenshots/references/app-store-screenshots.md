# App Store screenshot delivery

Use this reference only for Apple App Store screenshot work. Reopen the official pages before every final export because accepted device sizes can change.

## Official sources

- Screenshot specifications: https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/
- Upload previews and screenshots: https://developer.apple.com/help/app-store-connect/manage-app-information/upload-app-previews-and-screenshots/
- Custom Product Pages: https://developer.apple.com/app-store/custom-product-pages/

## Current delivery rules

- Supply one to ten screenshots per supported device set and localization.
- Use JPEG, JPG, or PNG without transparency or an alpha channel.
- Export an exact accepted size from Apple's current table. Do not infer a size from a device marketing name.
- When the interface is consistent across sizes, Apple can scale the highest required resolution down to smaller displays.
- If the app supports iPad, include an accepted iPad screenshot set.
- App previews appear before screenshots regardless of media ordering.

## Campaign page ordering

1. Put the campaign-specific gameplay story first.
2. Keep each game-specific frame focused on one promise.
3. Add at most one or two broad app screenshots afterward when showing catalogue breadth helps conversion.
4. Exclude creator, task, or account-management screens from a player-acquisition page unless they are part of the campaign promise.

Validate the final files against the exact App Store Connect media slot before handoff. Fail with `app_store_screenshot_spec_mismatch` when any file is rejected by the current specification.
