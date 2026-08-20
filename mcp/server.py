from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

mcp = FastMCP("foundations-mcp")
tavily_client = TavilyClient()
README_PATH = Path(__file__).parent / "resources" / "langchain_mcp_adapters_README.md"


@mcp.tool()
def search_web(query: str) -> dict[str, Any]:
    """Search the web for information about LangChain, LangGraph, or LangSmith."""
    return tavily_client.search(query)


@mcp.resource("resource://langchain-mcp-adapters/README.md")
def local_readme() -> str:
    """Return the locally stored langchain-mcp-adapters README."""
    try:
        return README_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        return f"Unable to load the local README resource: {exc}"


@mcp.prompt()
def prompt() -> str:
    """Provide instructions for the LangChain MCP learning agent."""
    return """
You are a helpful assistant that answers questions about LangChain, LangGraph, and LangSmith.

You can use the search_web tool and the locally stored README resource supplied by the client.
If the question is unrelated to LangChain, LangGraph, or LangSmith, say:
"I'm sorry, I can only answer questions about LangChain, LangGraph and LangSmith."
"""


if __name__ == "__main__":
    mcp.run(transport="stdio")
