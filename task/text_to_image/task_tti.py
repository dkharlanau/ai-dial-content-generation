import asyncio
import base64
from datetime import datetime
from pathlib import Path

from task._models.custom_content import Attachment
from task._utils.constants import DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT, API_KEY
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


class Size:
    """The size of the generated image."""
    square: str = "1024x1024"
    height_rectangle: str = "1024x1792"
    width_rectangle: str = "1792x1024"


class Style:
    """
    The style of the generated image. Must be one of vivid or natural.
     - Vivid tends to produce hyper-real and dramatic images.
     - Natural leans towards softer and more authentic visuals.
    """
    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    """The quality of the image that will be generated."""
    standard: str = "standard"
    hd: str = "hd"


def _attachment_filename(attachment: Attachment) -> str:
    safe_title = (attachment.title or "generated_image").replace(" ", "_")
    extension = "bin"
    if attachment.type and "/" in attachment.type:
        extension = attachment.type.split("/")[-1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{safe_title}_{timestamp}.{extension}"


def _normalize_base64(data: str) -> bytes:
    cleaned = data.strip()
    padding = (-len(cleaned)) % 4
    if padding:
        cleaned += "=" * padding
    return base64.b64decode(cleaned)


async def _save_images(attachments: list[Attachment]):
    if not attachments:
        print("No attachments were returned by the generation request.")
        return

    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "generated_images"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Demonstrates how to resolve images either from inline base64 data or bucket URLs.
    async with DialBucketClient(api_key=API_KEY, base_url=DIAL_URL) as bucket_client:
        for attachment in attachments:
            image_bytes = None
            if attachment.url:
                image_bytes = await bucket_client.get_file(attachment.url)
            elif attachment.data and attachment.type and attachment.type.lower().startswith("image/"):
                try:
                    image_bytes = _normalize_base64(attachment.data)
                except Exception as exc:
                    print(f"Skipping invalid image data for '{attachment.title}': {exc}")

            if image_bytes is None:
                print(f"Skipping attachment without download data: {attachment}")
                continue

            file_name = _attachment_filename(attachment)
            destination = output_dir / file_name
            destination.write_bytes(image_bytes)
            print(f"Saved generated image to {destination}")


def _generate_with_model(model_name: str, prompt: str, custom_fields: dict[str, str] | None) -> list[Attachment]:
    client = DialModelClient(
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name=model_name,
        api_key=API_KEY
    )
    print(f"\nRequesting image generation using model '{model_name}' ...")
    try:
        response = client.get_completion([Message(role=Role.USER, content=prompt)], custom_fields=custom_fields)
    except Exception as exc:
        if custom_fields:
            print(f"Model '{model_name}' rejected custom fields ({exc}), retrying without additional configuration.")
            response = client.get_completion([Message(role=Role.USER, content=prompt)], custom_fields=None)
        else:
            raise

    if response.custom_content:
        return response.custom_content.attachments

    print("Model response did not return any attachments.")
    return []


def start() -> None:
    prompt = "Sunny day on Bali with turquoise waters, palm trees swaying, and surfers on the horizon."
    generation_targets: list[tuple[str, dict[str, str] | None]] = [
        ("dall-e-3", None),
        (
            "imagegeneration@005",
            {
                "size": Size.width_rectangle,
                "quality": Quality.standard,
                "style": Style.vivid,
            }
        ),
    ]

    # Show how different deployments respond and how we handle optional options.
    for model_name, custom_fields in generation_targets:
        attachments = _generate_with_model(
            model_name=model_name,
            prompt=prompt,
            custom_fields=custom_fields
        )
        asyncio.run(_save_images(attachments))


if __name__ == "__main__":
    start()
