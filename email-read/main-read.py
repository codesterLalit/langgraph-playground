from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState
from langchain.tools import tool

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
