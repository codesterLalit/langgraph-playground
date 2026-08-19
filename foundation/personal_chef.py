import argparse
import base64
import mimetypes
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from tavily import TavilyClient

load_dotenv()

tavily_client = TavilyClient()

@tool
def web_search(query: str) -> Dict[str, Any]:
    """Search the web for recipes and cooking information."""
    return tavily_client.search(query)

SYSTEM_PROMPT = """
You are a personal chef. The user will give you a list of ingredients they have left over in their house,
or an image of their ingredients.

Using the web search tool, search the web for recipes that can be made with the ingredients they have.

Return recipe suggestions and eventually the recipe instructions to the user, if requested.
"""

def create_personal_chef():
    return create_agent(
        model="gpt-5-nano",
        tools=[web_search],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )

def image_message(image_path: Path, question: str) -> HumanMessage:
    image_bytes = image_path.read_bytes()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = mimetypes.guess_type(image_path.name)[0] or "image/png"

    return HumanMessage(
        content=[
            {"type": "text", "text": question},
            {"type": "image", "base64": image_base64, "mime_type": mime_type},
        ]
    )

def main() -> None:
    parser = argparse.ArgumentParser(description="Ask a personal chef agent for recipe ideas.")
    parser.add_argument(
        "question",
        nargs="?",
        default="I have some leftovers. What can I make?",
        help="The question or ingredient description to send to the chef.",
    )
    parser.add_argument(
        "--image",
        type=Path,
        help="Path to an image of the available ingredients.",
    )
    parser.add_argument(
        "--thread-id",
        default="personal-chef",
        help="Conversation thread identifier for the in-memory checkpointer.",
    )
    args = parser.parse_args()

    if args.image is not None:
        if not args.image.is_file():
            parser.error(f"Image file does not exist: {args.image}")
        message = image_message(args.image, args.question)
    else:
        message = HumanMessage(content=args.question)

    agent = create_personal_chef()
    response = agent.invoke(
        {"messages": [message]},
        {"configurable": {"thread_id": args.thread_id}},
    )
    print(response["messages"][-1].content)

if __name__ == "__main__":
    main()
