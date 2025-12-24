## Learning Notes – AI DIAL Content Generation

1. **OpenAI-style image analysis** (`task/image_to_text/openai/task_openai_itt.py`)
   - Built a `ContentedMessage` that bundles text prompts and image references (either base64 data URLs or remote URLs) so the DIAL gateway can convert it for OpenAI, Claude, or Gemini deployments.
   - Practiced instantiating `DialModelClient`, printing request metadata, and reading the `Message` that comes back to understand multimodal payload handling across vendors.

2. **DIAL bucket image analysis** (`task/image_to_text/task_dial_itt.py`)
   - Uploaded `dialx-banner.png` to the DIAL bucket via `DialBucketClient`, captured the attachment URL, and referenced it through `CustomContent`.
   - Learned how DIAL adapts attachment-based messages for whichever deployment I call, so I can compare GPT-4o versus other vendor responses without reencoding the image.

3. **Text-to-image generation** (`task/text_to_image/task_tti.py`)
   - Requested both DALL·E 3 and `imagegeneration@005`, handling `custom_fields` (size/quality/style) while also having a fallback when a deployment rejects those parameters.
   - Downloaded attachments by either decoding inline base64 (with padding normalization) or hitting the bucket file URL, and saved them with timestamped filenames to surface the generated results.

## Next steps before publishing
- Ensure `DIAL_API_KEY` is set (README already mentions `DIAL_API_KEY` env variable).  
- Gather the generated images under `generated_images/` for the demos.  
- Document the failures (403/500) I encountered and how I handled them so reviewers see the learning curve.
