import sys
from pathlib import Path
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient


ROOT = Path(__file__).resolve().parents[2]
LOCAL_MCP_SERVER = ROOT / "code" / "mcp" / "server.py"


def server_config(timezone: str = "America/New_York") -> dict[str, dict[str, Any]]:
    return {
        "local": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(LOCAL_MCP_SERVER)],
        },
        "time": {
            "transport": "stdio",
            "command": "uv",
            "args": ["run", "python", "-m", "mcp_server_time", f"--local-timezone={timezone}"],
        },
        "travel": {
            "transport": "streamable_http",
            "url": "https://mcp.kiwi.com",
        },
    }


def make_client(timezone: str = "America/New_York") -> MultiServerMCPClient:
    return MultiServerMCPClient(server_config(timezone))
