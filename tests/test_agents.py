"""Tests for agents module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from wetwire_core.agents import (
    AIConversationHandler,
    DeveloperAgent,
    RunnerAgent,
    ToolResult,
    detect_existing_package,
)


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_tool_result_creation(self):
        """Test that ToolResult can be created with all fields."""
        result = ToolResult(
            tool_use_id="tool_123",
            content="Operation successful",
            is_error=False,
            tool_name="init_package",
        )
        assert result.tool_use_id == "tool_123"
        assert result.content == "Operation successful"
        assert result.is_error is False
        assert result.tool_name == "init_package"

    def test_tool_result_default_values(self):
        """Test ToolResult default values."""
        result = ToolResult(
            tool_use_id="tool_123",
            content="Success",
        )
        assert result.is_error is False
        assert result.tool_name == ""


class TestDeveloperAgent:
    """Tests for DeveloperAgent class."""

    def test_get_system_prompt_includes_persona(self):
        """Test that get_system_prompt includes persona instructions."""
        agent = DeveloperAgent(
            persona_name="expert",
            persona_instructions="You are an expert who demands precision.",
        )
        system_prompt = agent.get_system_prompt()

        assert "You are an expert who demands precision." in system_prompt
        assert "developer" in system_prompt.lower()

    @patch("wetwire_core.agents.anthropic.Anthropic")
    def test_respond_returns_string(self, mock_anthropic):
        """Test that respond() returns a string response."""
        # Mock the API response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="I need a VPC with public subnets.")]
        mock_client.messages.create.return_value = mock_response

        agent = DeveloperAgent(
            persona_name="beginner",
            persona_instructions="You are a beginner.",
            client=mock_client,
        )

        response = agent.respond("What infrastructure do you need?")

        assert isinstance(response, str)
        assert response == "I need a VPC with public subnets."
        assert len(agent.conversation) == 2  # User message + assistant response


class TestRunnerAgent:
    """Tests for RunnerAgent class."""

    def test_initialization_with_existing_package(self):
        """Test RunnerAgent initialization with existing package."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            agent = RunnerAgent(
                output_dir=output_dir,
                existing_package="my_package",
            )
            assert agent.package_name == "my_package"
            assert agent.existing_package == "my_package"

    def test_initialization_without_existing_package(self):
        """Test RunnerAgent initialization without existing package."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            agent = RunnerAgent(output_dir=output_dir)
            assert agent.package_name == ""
            assert agent.existing_package is None

    def test_get_tools_returns_valid_definitions(self):
        """Test that get_tools returns valid tool definitions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            agent = RunnerAgent(output_dir=output_dir)
            tools = agent.get_tools()

            assert isinstance(tools, list)
            assert len(tools) == 6

            tool_names = [t["name"] for t in tools]
            assert "init_package" in tool_names
            assert "write_file" in tool_names
            assert "read_file" in tool_names
            assert "run_lint" in tool_names
            assert "run_build" in tool_names
            assert "ask_developer" in tool_names

            # Check that each tool has required fields
            for tool in tools:
                assert "name" in tool
                assert "description" in tool
                assert "input_schema" in tool

    def test_execute_tool_init_package_success(self):
        """Test execute_tool for init_package with success."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            agent = RunnerAgent(output_dir=output_dir)

            with patch("wetwire_core.agents.subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0, stderr="")

                result = agent.execute_tool(
                    "init_package",
                    {"package_name": "test_pkg", "description": "Test package"},
                )

                assert result.tool_name == "init_package"
                assert result.is_error is False
                assert "test_pkg" in result.content
                assert agent.package_name == "test_pkg"

    def test_execute_tool_init_package_failure(self):
        """Test execute_tool for init_package with failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            agent = RunnerAgent(output_dir=output_dir)

            with patch("wetwire_core.agents.subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=1, stderr="Error: invalid name")

                result = agent.execute_tool(
                    "init_package",
                    {"package_name": "invalid pkg", "description": "Test"},
                )

                assert result.is_error is True
                assert "Failed" in result.content

    def test_execute_tool_write_file_success(self):
        """Test execute_tool for write_file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            package_dir = output_dir / "test_pkg"
            package_dir.mkdir()

            agent = RunnerAgent(output_dir=output_dir)
            agent.package_name = "test_pkg"
            agent._package_dir = package_dir

            result = agent.execute_tool(
                "write_file",
                {"filename": "resources.py", "content": "# Test content\n"},
            )

            assert result.is_error is False
            assert "resources.py" in result.content
            assert (package_dir / "resources.py").exists()
            assert (package_dir / "resources.py").read_text() == "# Test content\n"

    def test_execute_tool_write_file_no_package(self):
        """Test execute_tool for write_file when no package initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            agent = RunnerAgent(output_dir=output_dir)

            result = agent.execute_tool(
                "write_file",
                {"filename": "test.py", "content": "test"},
            )

            assert result.is_error is True
            assert "Must init_package first" in result.content

    def test_execute_tool_read_file_success(self):
        """Test execute_tool for read_file when file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            package_dir = output_dir / "test_pkg"
            package_dir.mkdir()
            (package_dir / "test.py").write_text("test content")

            agent = RunnerAgent(output_dir=output_dir)
            agent.package_name = "test_pkg"
            agent._package_dir = package_dir

            result = agent.execute_tool("read_file", {"filename": "test.py"})

            assert result.is_error is False
            assert "test content" in result.content

    def test_execute_tool_read_file_missing(self):
        """Test execute_tool for read_file when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            package_dir = output_dir / "test_pkg"
            package_dir.mkdir()

            agent = RunnerAgent(output_dir=output_dir)
            agent.package_name = "test_pkg"
            agent._package_dir = package_dir

            result = agent.execute_tool("read_file", {"filename": "missing.py"})

            assert result.is_error is True
            assert "not found" in result.content.lower()

    def test_execute_tool_run_lint_pass(self):
        """Test execute_tool for run_lint when lint passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            package_dir = output_dir / "test_pkg"
            package_dir.mkdir()

            agent = RunnerAgent(output_dir=output_dir)
            agent.package_name = "test_pkg"
            agent._package_dir = package_dir

            with patch("wetwire_core.agents.subprocess.run") as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

                result = agent.execute_tool("run_lint", {})

                assert result.is_error is False
                assert "passed" in result.content.lower()

    def test_execute_tool_run_lint_fail(self):
        """Test execute_tool for run_lint when lint fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            package_dir = output_dir / "test_pkg"
            package_dir.mkdir()

            agent = RunnerAgent(output_dir=output_dir)
            agent.package_name = "test_pkg"
            agent._package_dir = package_dir

            with patch("wetwire_core.agents.subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stdout="Error: Missing import",
                    stderr="",
                )

                result = agent.execute_tool("run_lint", {})

                assert result.is_error is False  # Lint failures are not errors
                assert "found issues" in result.content.lower()

    def test_execute_tool_run_build_success(self):
        """Test execute_tool for run_build when build succeeds."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            package_dir = output_dir / "test_pkg"
            package_dir.mkdir()

            agent = RunnerAgent(output_dir=output_dir)
            agent.package_name = "test_pkg"
            agent._package_dir = package_dir

            with patch("wetwire_core.agents.subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout="AWSTemplateFormatVersion: '2010-09-09'",
                    stderr="",
                )

                result = agent.execute_tool("run_build", {})

                assert result.is_error is False
                assert "successful" in result.content.lower()

    def test_execute_tool_run_build_failure(self):
        """Test execute_tool for run_build when build fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            package_dir = output_dir / "test_pkg"
            package_dir.mkdir()

            agent = RunnerAgent(output_dir=output_dir)
            agent.package_name = "test_pkg"
            agent._package_dir = package_dir

            with patch("wetwire_core.agents.subprocess.run") as mock_run:
                mock_run.return_value = Mock(
                    returncode=1,
                    stdout="",
                    stderr="Error: Invalid resource",
                )

                result = agent.execute_tool("run_build", {})

                assert result.is_error is True
                assert "failed" in result.content.lower()

    def test_execute_tool_ask_developer(self):
        """Test execute_tool for ask_developer formats question."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            agent = RunnerAgent(output_dir=output_dir)

            result = agent.execute_tool(
                "ask_developer",
                {"question": "What region should I use?"},
            )

            assert "QUESTION:" in result.content
            assert "What region should I use?" in result.content


class TestAIConversationHandler:
    """Tests for AIConversationHandler class."""

    def test_lint_enforcement_write_file_requires_run_lint(self):
        """Test that writing a file without running lint triggers enforcement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            # Create mock developer and runner
            with patch("wetwire_core.agents.DeveloperAgent") as MockDev, patch(
                "wetwire_core.agents.RunnerAgent"
            ) as MockRunner:
                mock_dev = MagicMock()
                mock_runner = MagicMock()
                MockDev.return_value = mock_dev
                MockRunner.return_value = mock_runner

                # Simulate runner writing a file without running lint
                mock_runner.package_name = "test_pkg"
                mock_runner.run_turn.return_value = (
                    "I wrote the file",
                    [ToolResult("1", "Wrote resources.py", False, "write_file")],
                )

                handler = AIConversationHandler(
                    prompt="Create a bucket",
                    persona_name="beginner",
                    persona_instructions="You are a beginner",
                    output_dir=output_dir,
                )

                # Run one iteration - should detect missing lint
                handler.run()

                # Check that enforcement message was added
                system_messages = [m for m in handler.messages if m.role == "system"]
                assert any("run_lint" in m.content for m in system_messages)


class TestDetectExistingPackage:
    """Tests for detect_existing_package function."""

    def test_detect_package_with_setup_resources(self):
        """Test detection of valid wetwire package."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "my_package"
            package_dir.mkdir()
            (package_dir / "__init__.py").write_text("def setup_resources():\n    pass\n")
            (package_dir / "resources.py").write_text("# Resources\n")
            (package_dir / "network.py").write_text("# Network\n")

            package_name, files = detect_existing_package(package_dir)

            assert package_name == "my_package"
            assert "resources.py" in files
            assert "network.py" in files
            assert "__init__.py" not in files

    def test_detect_no_package_missing_init(self):
        """Test that directories without __init__.py are not detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "not_a_package"
            package_dir.mkdir()

            package_name, files = detect_existing_package(package_dir)

            assert package_name is None
            assert files == []

    def test_detect_no_package_missing_setup_resources(self):
        """Test that packages without setup_resources are not detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "not_wetwire"
            package_dir.mkdir()
            (package_dir / "__init__.py").write_text("# Regular package\n")

            package_name, files = detect_existing_package(package_dir)

            assert package_name is None
            assert files == []

    def test_detect_package_empty_directory(self):
        """Test detection in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "empty"
            package_dir.mkdir()

            package_name, files = detect_existing_package(package_dir)

            assert package_name is None
            assert files == []
