# Unified Learning App

This folder contains a CLI-first application that combines the core LangChain and LangGraph topics from modules 1-3.

## Setup

From the repository root:

```powershell
Copy-Item code\.env.example code\.env
uv sync
```

Set `OPENAI_API_KEY` and `TAVILY_API_KEY` in `code/.env` for model, web-search, chef, and MCP workflows.

## Commands

Run commands from `code/`:

```powershell
uv run python -m app.cli init
uv run python -m app.cli inbox
uv run python -m app.cli sql "SELECT COUNT(*) AS count FROM inbox_messages"
uv run python -m app.cli chat "What is in my inbox?"
uv run python -m app.cli chef "Suggest dinner using tomatoes and rice"
uv run python -m app.cli chef --image path\to\ingredients.png "What can I make?"
uv run python -m app.cli handbook "What is the vacation policy?"
uv run python -m app.cli mcp
uv run python -m app.cli mcp-chat "What is LangChain MCP?"
```

The email demo is local and does not send real messages:

```powershell
uv run python -m app.cli email inbox
uv run python -m app.cli email draft jane@example.com "Re: coffee" "That works for me."
uv run python -m app.cli email review 1 approve
```

SQLite defaults to `code/data/app.db`; set `APP_SQLITE_PATH` to override it. The local MCP server provides a web-search tool, prompt, and checked-in README resource. The configured third-party MCPs are Kiwi travel and `mcp_server_time`.

The existing notebooks remain the detailed lessons. Audio recording, provider comparisons, and the Next.js UI are intentionally separate from this first CLI milestone.
