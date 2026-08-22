from dataclasses import dataclass
from typing import Callable

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langgraph.types import Command

load_dotenv()


@dataclass
class EmailContext:
	email_address: str = "julie@example.com"
	password: str = "password123"


class AuthenticatedState(AgentState):
	authenticated: bool


@tool
def check_inbox() -> str:
	"""Check the inbox for recent emails."""
	return """Hi Julie,

I'm going to be in town next week and was wondering if we could grab a coffee?

- best, Jane (jane@example.com)
"""


@tool
def send_email(to: str, subject: str, body: str) -> str:
	"""Send an email reply."""
	return f"Email sent to {to} with subject {subject} and body {body}"


@tool
def authenticate(email: str, password: str, runtime: ToolRuntime) -> Command:
	"""Authenticate the user before allowing inbox access or email sending."""
	authenticated = (
		email == runtime.context.email_address
		and password == runtime.context.password
	)
	message = (
		"Successfully authenticated"
		if authenticated
		else "Authentication failed"
	)
	return Command(
		update={
			"authenticated": authenticated,
			"messages": [ToolMessage(message, tool_call_id=runtime.tool_call_id)],
		}
	)


@wrap_model_call
async def dynamic_tool_call(
	request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
	"""Expose protected tools only after successful authentication."""
	tools = [check_inbox, send_email] if request.state.get("authenticated") else [authenticate]
	return await handler(request.override(tools=tools))
