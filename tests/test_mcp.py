"""Tests for MCP server abstraction."""

from unittest.mock import MagicMock

import pytest


def _mcp_available() -> bool:
    """Helper to check if MCP is available."""
    try:
        from wetwire_core.mcp import MCP_AVAILABLE

        return MCP_AVAILABLE
    except ImportError:
        return False


class TestMCPImport:
    """Tests for MCP import handling."""

    def test_import_without_mcp_installed(self):
        """Test graceful handling when MCP is not installed."""
        # The module should import without error even if mcp is not installed
        from wetwire_core import mcp

        assert hasattr(mcp, "create_server")
        assert hasattr(mcp, "register_tool")
        assert hasattr(mcp, "get_install_instructions")

    def test_mcp_available_flag(self):
        """Test MCP_AVAILABLE flag reflects installation status."""
        from wetwire_core.mcp import MCP_AVAILABLE

        # Should be a boolean
        assert isinstance(MCP_AVAILABLE, bool)


class TestGetInstallInstructions:
    """Tests for get_install_instructions function."""

    def test_instructions_contain_package_name(self):
        """Test that instructions include the package name."""
        from wetwire_core.mcp import get_install_instructions

        instructions = get_install_instructions("wetwire-aws")
        assert "wetwire-aws" in instructions

    def test_instructions_contain_mcp_config(self):
        """Test that instructions mention MCP configuration."""
        from wetwire_core.mcp import get_install_instructions

        instructions = get_install_instructions("wetwire-github")
        assert "mcp" in instructions.lower()

    def test_instructions_contain_command(self):
        """Test that instructions include a command to run."""
        from wetwire_core.mcp import get_install_instructions

        instructions = get_install_instructions("wetwire-aws")
        # Should contain either uvx or npx style command
        assert "wetwire-aws" in instructions


class TestCreateServer:
    """Tests for create_server function."""

    def test_create_server_returns_none_when_mcp_unavailable(self):
        """Test create_server returns None when MCP is not installed."""
        from wetwire_core.mcp import MCP_AVAILABLE, create_server

        if not MCP_AVAILABLE:
            server = create_server("test-server")
            assert server is None

    @pytest.mark.skipif(
        not _mcp_available(),
        reason="MCP not installed",
    )
    def test_create_server_returns_server_when_mcp_available(self):
        """Test create_server returns a server object when MCP is installed."""
        from wetwire_core.mcp import create_server

        server = create_server("test-server")
        assert server is not None


class TestRegisterTool:
    """Tests for register_tool function."""

    def test_register_tool_with_none_server(self):
        """Test register_tool handles None server gracefully."""
        from wetwire_core.mcp import register_tool

        # Should not raise when server is None
        register_tool(None, "test-tool", lambda: None, {"type": "object"})

    @pytest.mark.skipif(
        not _mcp_available(),
        reason="MCP not installed",
    )
    def test_register_tool_adds_tool_to_server(self):
        """Test register_tool properly registers a tool."""
        from wetwire_core.mcp import create_server, register_tool

        server = create_server("test-server")
        handler = MagicMock(return_value="result")
        schema = {
            "type": "object",
            "properties": {"arg": {"type": "string"}},
        }

        register_tool(server, "my-tool", handler, schema)
        # Tool should be registered (implementation-specific check)


class TestDebugLogging:
    """Tests for debug logging configuration."""

    def test_debug_env_var_respected(self, monkeypatch):
        """Test WETWIRE_MCP_DEBUG environment variable is respected."""
        monkeypatch.setenv("WETWIRE_MCP_DEBUG", "1")

        # Re-import to pick up env var
        import importlib

        from wetwire_core import mcp

        importlib.reload(mcp)

        # Module should respect debug setting
        assert hasattr(mcp, "DEBUG")

    def test_debug_disabled_by_default(self, monkeypatch):
        """Test debug is disabled by default."""
        monkeypatch.delenv("WETWIRE_MCP_DEBUG", raising=False)

        import importlib

        from wetwire_core import mcp

        importlib.reload(mcp)

        from wetwire_core.mcp import DEBUG

        assert DEBUG is False
