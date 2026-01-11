"""Tests for Kiro CLI integration."""

from unittest.mock import MagicMock, patch


class TestKiroConfig:
    """Tests for KiroConfig dataclass."""

    def test_kiro_config_exists(self):
        """Test that KiroConfig is defined."""
        from wetwire_core.kiro import KiroConfig

        assert KiroConfig is not None

    def test_kiro_config_creation(self):
        """Test creating a KiroConfig."""
        from wetwire_core.kiro import KiroConfig

        config = KiroConfig(
            agent_name="wetwire-runner",
            agent_prompt="You are a runner agent.",
            mcp_command="wetwire-aws-mcp",
        )
        assert config.agent_name == "wetwire-runner"
        assert config.agent_prompt == "You are a runner agent."
        assert config.mcp_command == "wetwire-aws-mcp"

    def test_kiro_config_optional_fields(self):
        """Test KiroConfig with optional fields."""
        from wetwire_core.kiro import KiroConfig

        config = KiroConfig(
            agent_name="test-agent",
            agent_prompt="Test prompt",
            mcp_command="test-mcp",
            mcp_args=["--debug"],
        )
        assert config.mcp_args == ["--debug"]


class TestKiroInstaller:
    """Tests for Kiro configuration installer."""

    def test_generate_mcp_config(self):
        """Test generating MCP configuration JSON."""
        from wetwire_core.kiro import KiroConfig, generate_mcp_config

        config = KiroConfig(
            agent_name="wetwire-runner",
            agent_prompt="Test prompt",
            mcp_command="wetwire-aws-mcp",
        )

        mcp_config = generate_mcp_config(config)

        assert "mcpServers" in mcp_config
        assert config.mcp_command in str(mcp_config)

    def test_generate_agent_config(self):
        """Test generating agent configuration JSON."""
        from wetwire_core.kiro import KiroConfig, generate_agent_config

        config = KiroConfig(
            agent_name="wetwire-runner",
            agent_prompt="You are a runner agent.",
            mcp_command="wetwire-aws-mcp",
        )

        agent_config = generate_agent_config(config)

        assert "name" in agent_config
        assert agent_config["name"] == "wetwire-runner"
        assert "systemPrompt" in agent_config or "prompt" in agent_config

    def test_install_configs(self, tmp_path):
        """Test installing Kiro configurations to disk."""
        from wetwire_core.kiro import KiroConfig, install_configs

        config = KiroConfig(
            agent_name="wetwire-runner",
            agent_prompt="Test prompt",
            mcp_command="wetwire-aws-mcp",
        )

        project_dir = tmp_path / "project"
        project_dir.mkdir()
        home_dir = tmp_path / "home"
        home_dir.mkdir()

        install_configs(config, project_dir=project_dir, home_dir=home_dir)

        # Check MCP config was created
        mcp_config_path = project_dir / ".kiro" / "mcp.json"
        assert mcp_config_path.exists()

        # Check agent config was created
        agent_config_path = home_dir / ".kiro" / "agents" / f"{config.agent_name}.json"
        assert agent_config_path.exists()


class TestKiroLauncher:
    """Tests for Kiro CLI launcher."""

    def test_build_kiro_command(self):
        """Test building kiro CLI command."""
        from wetwire_core.kiro import build_kiro_command

        command = build_kiro_command(agent_name="wetwire-runner", prompt="Create S3")

        assert "kiro-cli" in command or "kiro" in command
        assert "wetwire-runner" in command

    @patch("subprocess.run")
    def test_launch_kiro(self, mock_run):
        """Test launching Kiro CLI."""
        from wetwire_core.kiro import KiroConfig, launch_kiro

        mock_run.return_value = MagicMock(returncode=0)

        config = KiroConfig(
            agent_name="wetwire-runner",
            agent_prompt="Test prompt",
            mcp_command="wetwire-aws-mcp",
        )

        launch_kiro(config, prompt="Create S3 bucket")

        mock_run.assert_called_once()


class TestKiroAvailable:
    """Tests for Kiro availability detection."""

    def test_kiro_available_flag(self):
        """Test KIRO_AVAILABLE flag exists."""
        from wetwire_core.kiro import KIRO_AVAILABLE

        assert isinstance(KIRO_AVAILABLE, bool)

    @patch("shutil.which")
    def test_check_kiro_installed(self, mock_which):
        """Test checking if Kiro CLI is installed."""
        from wetwire_core.kiro import check_kiro_installed

        # When kiro-cli is found
        mock_which.return_value = "/usr/local/bin/kiro-cli"
        assert check_kiro_installed() is True

        # When kiro-cli is not found
        mock_which.return_value = None
        assert check_kiro_installed() is False
