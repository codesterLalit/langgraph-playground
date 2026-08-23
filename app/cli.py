import argparse
import asyncio
from pathlib import Path

from .config import settings
from .database import Database
from .sql_tools import make_sql_tool


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lc-foundations",
        description="Unified LangChain foundations learning app.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=settings.sqlite_path,
        help="SQLite database path.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize the SQLite database.")
    init_parser.set_defaults(handler=initialize_database)

    inbox_parser = subparsers.add_parser("inbox", help="Show the demo inbox.")
    inbox_parser.set_defaults(handler=show_inbox)

    thread_parser = subparsers.add_parser("thread", help="Show messages in a thread.")
    thread_parser.add_argument("thread_id")
    thread_parser.set_defaults(handler=show_thread)

    chat_parser = subparsers.add_parser("chat", help="Ask the LangChain assistant a question.")
    chat_parser.add_argument("question")
    chat_parser.add_argument("--thread-id", default="cli-chat")
    chat_parser.set_defaults(handler=chat)

    sql_parser = subparsers.add_parser("sql", help="Run a read-only query against SQLite.")
    sql_parser.add_argument("query")
    sql_parser.set_defaults(handler=run_sql)

    handbook_parser = subparsers.add_parser("handbook", help="Search the local employee handbook.")
    handbook_parser.add_argument("question")
    handbook_parser.set_defaults(handler=search_handbook)

    mcp_parser = subparsers.add_parser("mcp", help="Discover configured MCP capabilities.")
    mcp_parser.set_defaults(handler=discover_mcp)

    mcp_chat_parser = subparsers.add_parser("mcp-chat", help="Ask the MCP-powered assistant.")
    mcp_chat_parser.add_argument("question")
    mcp_chat_parser.add_argument("--thread-id", default="mcp-chat")
    mcp_chat_parser.set_defaults(handler=mcp_chat)

    chef_parser = subparsers.add_parser("chef", help="Ask the multimodal personal chef.")
    chef_parser.add_argument("question")
    chef_parser.add_argument("--image", type=Path)
    chef_parser.add_argument("--thread-id", default="chef")
    chef_parser.set_defaults(handler=chef)

    email_parser = subparsers.add_parser("email", help="Manage the safe local email demo.")
    email_commands = email_parser.add_subparsers(dest="email_command", required=True)
    email_inbox = email_commands.add_parser("inbox", help="Read the local demo inbox.")
    email_inbox.set_defaults(handler=email_inbox_command)
    email_draft = email_commands.add_parser("draft", help="Create an email draft.")
    email_draft.add_argument("recipient")
    email_draft.add_argument("subject")
    email_draft.add_argument("body")
    email_draft.set_defaults(handler=email_draft_command)
    email_review = email_commands.add_parser("review", help="Approve or reject a draft.")
    email_review.add_argument("message_id", type=int)
    email_review.add_argument("decision", choices=("approve", "reject"))
    email_review.set_defaults(handler=email_review_command)
    return parser


def initialize_database(database: Database, _args: argparse.Namespace) -> None:
    database.initialize()
    database.seed_inbox()
    print(f"Initialized SQLite database at {database.path}")


def show_inbox(database: Database, _args: argparse.Namespace) -> None:
    database.initialize()
    database.seed_inbox()
    for message in database.list_inbox():
        print(f"[{message['id']}] {message['sender']} - {message['subject']}")
        print(message["body"])


def show_thread(database: Database, args: argparse.Namespace) -> None:
    database.initialize()
    messages = database.list_messages(args.thread_id)
    if not messages:
        print(f"No messages found for thread '{args.thread_id}'.")
        return
    for message in messages:
        print(f"{message['role']}: {message['content']}")


def chat(database: Database, args: argparse.Namespace) -> None:
    from .agents import ask_agent, make_chat_agent

    database.initialize()
    answer = asyncio.run(ask_agent(make_chat_agent(database), args.question, args.thread_id))
    database.add_message(args.thread_id, "user", args.question)
    database.add_message(args.thread_id, "assistant", answer)
    print(answer)


def run_sql(database: Database, args: argparse.Namespace) -> None:
    database.initialize()
    result = make_sql_tool(database.path).invoke({"query": args.query})
    print(result)


def discover_mcp(_database: Database, _args: argparse.Namespace) -> None:
    from .mcp_integration import make_client

    async def discover() -> None:
        client = make_client(settings.mcp_timezone)
        try:
            tools = await client.get_tools()
            for tool in tools:
                print(tool.name)
        except Exception as exc:
            print(f"MCP discovery failed: {exc}")

    asyncio.run(discover())


def search_handbook(_database: Database, args: argparse.Namespace) -> None:
    from .rag import HandbookSearch

    handbook_path = (
        Path(__file__).resolve().parents[2]
        / "notebooks"
        / "module-2"
        / "resources"
        / "acmecorp-employee-handbook.pdf"
    )
    print(HandbookSearch(handbook_path).search(args.question))


def mcp_chat(_database: Database, args: argparse.Namespace) -> None:
    from .workflows import run_mcp_agent

    print(asyncio.run(run_mcp_agent(args.question, args.thread_id)))


def chef(_database: Database, args: argparse.Namespace) -> None:
    from .workflows import run_chef_agent

    print(asyncio.run(run_chef_agent(args.question, args.image, args.thread_id)))


def email_inbox_command(database: Database, _args: argparse.Namespace) -> None:
    database.initialize()
    database.seed_inbox()
    show_inbox(database, _args)


def email_draft_command(database: Database, args: argparse.Namespace) -> None:
    database.initialize()
    message_id = database.add_outbox(args.recipient, args.subject, args.body)
    print(f"Draft {message_id} created with status pending.")


def email_review_command(database: Database, args: argparse.Namespace) -> None:
    database.initialize()
    database.review_outbox(args.message_id, args.decision == "approve")
    print(f"Draft {args.message_id}: {args.decision}d.")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    database = Database(args.db)
    args.handler(database, args)


if __name__ == "__main__":
    main()
