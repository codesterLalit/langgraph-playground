from dataclasses import dataclass
from typing import Any

from langchain.agents import AgentState, create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from .config import settings
from .database import Database


@dataclass
class UserContext:
    user_id: str = "local-user"
    language: str = "English"
    role: str = "external"


class AppState(AgentState):
    authenticated: bool


def make_model_agent(tools: list[Any], system_prompt: str):
    return create_agent(
        model=settings.model_name,
        tools=tools,
        system_prompt=system_prompt,
        context_schema=UserContext,
        state_schema=AppState,
        checkpointer=InMemorySaver(),
    )


def make_email_tools(database: Database) -> list[Any]:
    @tool
    def check_inbox() -> str:
        """Read recent messages from the local demo inbox."""
        rows = database.list_inbox()
        if not rows:
            return "The inbox is empty."
        return "\n\n".join(
            f"From: {row['sender']}\nSubject: {row['subject']}\n{row['body']}"
            for row in rows
        )

    @tool
    def save_email_draft(to: str, subject: str, body: str) -> str:
        """Save an email draft for human approval; never sends it externally."""
        message_id = database.add_outbox(to, subject, body)
        return f"Draft {message_id} saved and awaiting human approval."

    return [check_inbox, save_email_draft]


def make_chat_agent(database: Database):
    return make_model_agent(
        make_email_tools(database),
        "You are a helpful local learning assistant. Explain your work clearly. "
        "You can read the demo inbox and save email drafts for approval.",
    )


async def ask_agent(agent: Any, question: str, thread_id: str) -> str:
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content=question)]},
        config={"configurable": {"thread_id": thread_id}},
        context=UserContext(),
    )
    return str(response["messages"][-1].content)
