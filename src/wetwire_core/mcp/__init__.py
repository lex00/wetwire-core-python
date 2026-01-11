"""MCP server abstraction for wetwire domain packages.

This module provides utilities for creating MCP (Model Context Protocol) servers
with reduced boilerplate. It handles graceful fallback when MCP is not installed.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from typing import Any

# Check for debug mode
DEBUG = os.environ.get("WETWIRE_MCP_DEBUG", "").lower() in ("1", "true", "yes")

# Configure logging based on debug flag
if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("wetwire.mcp")
    logger.setLevel(logging.DEBUG)
else:
    logger = logging.getLogger("wetwire.mcp")

# Try to import MCP, but handle gracefully if not installed
MCP_AVAILABLE = False
_Server: type[Any] | None = None
_stdio_server: Callable[..., Any] | None = None

try:
    from mcp.server import Server as _MCPServer  # type: ignore[import-not-found]
    from mcp.server.stdio import stdio_server as _mcp_stdio_server  # type: ignore[import-not-found]

    MCP_AVAILABLE = True
    _Server = _MCPServer
    _stdio_server = _mcp_stdio_server
except ImportError:
    pass


def get_install_instructions(package_name: str) -> str:
    """Get installation instructions for MCP server integration.

    Args:
        package_name: Name of the wetwire domain package (e.g., 'wetwire-aws').

    Returns:
        Human-readable instructions for configuring MCP.
    """
    return f"""To use {package_name} as an MCP server, add the following to your MCP configuration:

{{
  "mcpServers": {{
    "{package_name}": {{
      "command": "uvx",
      "args": ["{package_name}-mcp"]
    }}
  }}
}}

Or if using npx:

{{
  "mcpServers": {{
    "{package_name}": {{
      "command": "npx",
      "args": ["-y", "{package_name}-mcp"]
    }}
  }}
}}
"""


def create_server(name: str) -> Any | None:
    """Create an MCP server instance.

    Args:
        name: Name of the MCP server.

    Returns:
        Server instance if MCP is available, None otherwise.
    """
    if not MCP_AVAILABLE or _Server is None:
        logger.warning("MCP is not installed. Server creation skipped.")
        return None

    logger.debug(f"Creating MCP server: {name}")
    return _Server(name)


def register_tool(
    server: Any | None,
    name: str,
    handler: Callable[..., Any],
    schema: dict[str, Any],
    description: str | None = None,
) -> None:
    """Register a tool with an MCP server.

    Args:
        server: MCP server instance (or None if MCP unavailable).
        name: Name of the tool.
        handler: Function to handle tool calls.
        schema: JSON schema for tool arguments.
        description: Optional description of the tool.
    """
    if server is None:
        logger.debug(f"Skipping tool registration for '{name}' (no server)")
        return

    logger.debug(f"Registering tool: {name}")

    # The actual registration depends on MCP's API
    # This is a simplified version that works with mcp.server.Server
    @server.call_tool()
    async def tool_wrapper(tool_name: str, arguments: dict[str, Any]) -> Any:
        if tool_name == name:
            return handler(**arguments)

    # Register the tool schema
    @server.list_tools()
    async def list_tools_wrapper() -> list[dict[str, Any]]:
        return [
            {
                "name": name,
                "description": description or f"Tool: {name}",
                "inputSchema": schema,
            }
        ]


async def run_server(server: Any | None) -> None:
    """Run the MCP server using stdio transport.

    Args:
        server: MCP server instance (or None if MCP unavailable).
    """
    if server is None or not MCP_AVAILABLE or _stdio_server is None:
        logger.error("Cannot run server: MCP is not available")
        return

    logger.info("Starting MCP server...")
    async with _stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


__all__ = [
    "MCP_AVAILABLE",
    "DEBUG",
    "create_server",
    "register_tool",
    "run_server",
    "get_install_instructions",
]
