# Apple App Preview delivery

Use this reference only for Apple App Preview work. Verify the official specification again immediately before export or upload.

## Official sources

- App Preview specifications: https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications/
- Upload previews and screenshots: https://developer.apple.com/help/app-store-connect/manage-app-information/upload-app-previews-and-screenshots/
- Show more with app previews: https://developer.apple.com/app-store/app-previews/

## Current technical contract

- Duration: 15 to 30 seconds.
- Maximum file size: 500 MB.
- Maximum frame rate: 30 fps.
- H.264: progressive, target 10 to 12 Mbps, up to High Profile Level 4.0.
- ProRes: ProRes 422 HQ in MOV.
- H.264 containers: MOV, M4V, or MP4.
- Audio: enabled stereo, 256 kbps AAC, 44.1 kHz or 48 kHz.
- Up to three previews may be delivered per supported device size and localization.
- A currently accepted iPhone portrait preview size is 886 x 1920.
- A currently accepted iPad landscape preview size is 1600 x 1200.

Apple can change accepted devices and dimensions. Validate the target slot against the current official table rather than treating these two common sizes as permanent.

## Delivery behavior

- App previews always appear before screenshots.
- Apple defaults the poster frame to approximately five seconds, but the frame should be chosen deliberately.
- Processing can take up to 24 hours. An uploaded asset can be complete while video delivery remains processing.
- Do not upload the same file again merely because processing is not finished.

Fail with `app_preview_spec_mismatch` if the media inspector disagrees with the current App Store Connect slot.
