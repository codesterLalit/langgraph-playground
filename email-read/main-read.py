from dataclasses import dataclass
from typing import Callable

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langchain.agents.middleware import (
	HumanInTheLoopMiddleware,
	ModelRequest,
	ModelResponse,
	dynamic_prompt,
	wrap_model_call,
)
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


@dynamic_prompt
def dynamic_prompt_func(request: ModelRequest) -> str:
	"""Change the assistant instructions with the authentication state."""
	if request.state.get("authenticated"):
		return "You are a helpful assistant that can check the inbox and send emails."
	return "You are a helpful assistant that can authenticate users."


agent = create_agent(
	"gpt-5-nano",
	tools=[authenticate, check_inbox, send_email],
	state_schema=AuthenticatedState,
	context_schema=EmailContext,
	middleware=[
		dynamic_tool_call,
		dynamic_prompt_func,
		HumanInTheLoopMiddleware(
			interrupt_on={
				"authenticate": False,
				"check_inbox": False,
				"send_email": True,
			}
		),
	],
)
