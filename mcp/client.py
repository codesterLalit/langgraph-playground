import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

SERVER_PATH = Path(__file__).with_name("server.py")


def mcp_client_config() -> dict[str, dict[str, Any]]:
    return {
        "local_server": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(SERVER_PATH)],
        }
    }


def resource_text(resources: list[Any]) -> str:
    """Convert MCP resource contents into text for the agent context."""
    parts: list[str] = []
    for resource in resources:
        content = getattr(resource, "content", resource)
        parts.append(str(content))
    return "\n\n".join(parts)


async def run_agent(question: str, thread_id: str) -> str:
    client = MultiServerMCPClient(mcp_client_config())

    tools = await client.get_tools()
    resources = await client.get_resources("local_server")
    prompts = await client.get_prompt("local_server", "prompt")

    system_prompt = prompts[0].content
    reference_material = resource_text(resources)
    system_prompt = (
        f"{system_prompt}\n\n"
        "Reference material from the MCP resource:\n"
        f"{reference_material}"
    )

    agent = create_agent(
        model="gpt-5-nano",
        tools=tools,
        system_prompt=system_prompt,
    )
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    return str(response["messages"][-1].content)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a LangChain agent with a local MCP server.")
    parser.add_argument("question", help="Question to ask the MCP-powered agent.")
    parser.add_argument(
        "--thread-id",
        default="mcp-client",
        help="Conversation thread identifier.",
    )
    args = parser.parse_args()
    print(asyncio.run(run_agent(args.question, args.thread_id)))


if __name__ == "__main__":
    main()
