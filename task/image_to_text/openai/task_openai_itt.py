import base64
from pathlib import Path
from typing import Iterable

from task._utils.constants import API_KEY, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.model_client import DialModelClient
from task._models.role import Role
from task.image_to_text.openai.message import ContentedMessage, TxtContent, ImgContent, ImgUrl


def _build_message(image_url: str) -> ContentedMessage:
    """Wrap text and image data into the OpenAI-style contented message.

    This demonstrates how to build a multimodal payload that DIAL can translate
    into OpenAI/Gemini/Claude formats.
    """
    return ContentedMessage(
        role=Role.USER,
        content=[
            TxtContent(text="What do you see in this picture?"),
            ImgContent(image_url=ImgUrl(url=image_url))
        ]
    )


def _run_analysis(model_name: str, image_url: str, label: str) -> None:
    client = DialModelClient(
        endpoint=DIAL_CHAT_COMPLETIONS_ENDPOINT,
        deployment_name=model_name,
        api_key=API_KEY
    )

    message = _build_message(image_url=image_url)
    print(f"\nAnalyzing '{label}' with model '{model_name}' ...")
    response = client.get_completion([message])
    print(f"AI: {response.content}")


def _iter_image_sources() -> Iterable[tuple[str, str]]:
    project_root = Path(__file__).parent.parent.parent.parent
    image_path = project_root / "dialx-banner.png"

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    yield "Base64 payload", f"data:image/png;base64,{base64_image}"
    yield "Remote file URL", "https://a-z-animals.com/media/2019/11/Elephant-male-1024x535.jpg"


def start() -> None:
    model_names = [
        "gpt-4o",
        # add more deployment names (e.g., Claude or Gemini) if you want to compare them
    ]

    for label, image_url in _iter_image_sources():
        # Print different interpretations to prove DIAL adapts the payload per model.
        for model in model_names:
            _run_analysis(model_name=model, image_url=image_url, label=label)


if __name__ == "__main__":
    start()
