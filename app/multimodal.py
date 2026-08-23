import base64
import mimetypes
from pathlib import Path

from langchain.messages import HumanMessage


def image_message(path: Path | str, question: str) -> HumanMessage:
    image_path = Path(path)
    if not image_path.is_file():
        raise FileNotFoundError(image_path)
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    mime_type = mimetypes.guess_type(image_path.name)[0] or "image/png"
    return HumanMessage(
        content=[
            {"type": "text", "text": question},
            {"type": "image", "base64": encoded, "mime_type": mime_type},
        ]
    )
