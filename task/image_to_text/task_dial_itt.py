import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


async def _put_image() -> Attachment:
    file_name = "dialx-banner.png"
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = "image/png"

    async with DialBucketClient(api_key=API_KEY, base_url=DIAL_URL) as bucket_client:
        with open(image_path, "rb") as image_file:
            raw_bytes = image_file.read()
        content = BytesIO(raw_bytes)
        upload_result = await bucket_client.put_file(
            name=file_name,
            mime_type=mime_type_png,
            content=content
        )

    attachment_url = (
        upload_result.get("url")
        or upload_result.get("path")
        or upload_result.get("file_url")
        or upload_result.get("uri")
    )
    if not attachment_url:
        raise ValueError("Bucket upload response did not return an attachment URL")

    # Return an attachment so we can test the DIAL bucket-based workflow.
    return Attachment(title=file_name, url=attachment_url, type=mime_type_png)


def _prepare_message(attachment: Attachment) -> Message:
    return Message(
        role=Role.USER,
        content="What do you see on this picture?",
        custom_content=CustomContent(attachments=[attachment])
    )


def _analyze_with_bucket(attachment: Attachment) -> None:
    models = [
        "gpt-4o",
        # add additional deployment names (e.g., Claude or Gemini) to compare responses
    ]

    for model in models:
        client = DialModelClient(
            endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
            deployment_name=model,
            api_key=API_KEY
        )
        message = _prepare_message(attachment)
        # Demonstrates the same bucket attachment flowing through multiple models.
        print(f"\nCalling model '{model}' with bucket attachment reference...")
        response = client.get_completion([message])
        print(f"AI: {response.content}")


def start() -> None:
    async def _run() -> None:
        attachment = await _put_image()
        print(f"Uploaded file '{attachment.title}' to bucket with url: {attachment.url}")
        _analyze_with_bucket(attachment)

    asyncio.run(_run())


if __name__ == "__main__":
    start()
