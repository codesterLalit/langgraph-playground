from pathlib import Path
from typing import Any

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from .config import settings
from .mcp_integration import make_client
from .multimodal import image_message


async def run_mcp_agent(question: str, thread_id: str) -> str:
    """Run an agent using tools and local resource context from the MCP servers."""
    client = make_client(settings.mcp_timezone)
    tools = await client.get_tools()
    resources = await client.get_resources("local")
    prompts = await client.get_prompt("local", "prompt")
    resource_text = "\n\n".join(
        str(getattr(resource, "content", resource)) for resource in resources
    )
    system_prompt = (
        f"{prompts[0].content}\n\n"
        "Local MCP reference material:\n"
        f"{resource_text}"
    )
    agent = create_agent(
        model=settings.model_name,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=InMemorySaver(),
    )
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    return str(response["messages"][-1].content)


async def run_chef_agent(question: str, image_path: Path | None, thread_id: str) -> str:
    """Run the multimodal personal chef workflow using Tavily search."""
    from tavily import TavilyClient
    from langchain.tools import tool

    tavily_client = TavilyClient()

    @tool
    def search_recipes(query: str) -> dict[str, Any]:
        """Search the web for recipes using the available ingredients."""
        return tavily_client.search(query)

    agent = create_agent(
        model=settings.model_name,
        tools=[search_recipes],
        system_prompt=(
            "You are a personal chef. Identify ingredients from text or images, "
            "then use search_recipes to suggest practical recipes."
        ),
        checkpointer=InMemorySaver(),
    )
    message = (
        image_message(image_path, question)
        if image_path is not None
        else HumanMessage(content=question)
    )
    response = await agent.ainvoke(
        {"messages": [message]},
        config={"configurable": {"thread_id": thread_id}},
    )
    return str(response["messages"][-1].content)
