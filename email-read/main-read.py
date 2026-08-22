import argparse
import asyncio
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


def print_approval_request(interrupts: list[Any]) -> None:
	"""Display the pending tool request before asking the user for approval."""
	for interrupt in interrupts:
		value = interrupt.value
		for action in value.get("action_requests", []):
			print(f"\nApproval required for: {action['name']}")
			print(f"Arguments: {action['args']}")


async def run_conversation(question: str, thread_id: str) -> str:
	config = {"configurable": {"thread_id": thread_id}}
	context = EmailContext()
	result = await agent.ainvoke(
		{"messages": [{"role": "user", "content": question}]},
		config=config,
		context=context,
	)

	while "__interrupt__" in result:
		print_approval_request(result["__interrupt__"])
		decision = input("Approve this action? [y/N]: ").strip().lower()
		if decision in {"y", "yes"}:
			resume = {"decisions": [{"type": "approve"}]}
		else:
			resume = {
				"decisions": [
					{"type": "reject", "message": "The user rejected this action."}
				]
			}
		result = await agent.ainvoke(
			Command(resume=resume),
			config=config,
			context=context,
		)

	return str(result["messages"][-1].content)


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Read an inbox and send replies with an authenticated email agent."
	)
	parser.add_argument("question", help="Request for the email assistant.")
	parser.add_argument(
		"--thread-id",
		default="email-read",
		help="Conversation identifier used by the agent checkpoint.",
	)
	args = parser.parse_args()
	print(asyncio.run(run_conversation(args.question, args.thread_id)))


if __name__ == "__main__":
	main()
