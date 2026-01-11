"""Kiro CLI integration for wetwire domain packages.

This module provides utilities for integrating with Kiro CLI,
enabling design mode with AWS-based AI providers.

Usage:
    from wetwire_core.kiro import KiroConfig, install_configs, launch_kiro

    config = KiroConfig(
        agent_name="wetwire-runner",
        agent_prompt="You are a runner agent...",
        mcp_command="wetwire-aws-mcp",
    )

    # Install Kiro configurations
    install_configs(config)

    # Launch Kiro CLI
    launch_kiro(config, prompt="Create S3 bucket")
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class KiroConfig:
    """Configuration for Kiro CLI integration.

    Attributes:
        agent_name: Name of the custom agent (e.g., "wetwire-runner").
        agent_prompt: System prompt for the agent.
        mcp_command: MCP server command (e.g., "wetwire-aws-mcp").
        mcp_args: Optional arguments for MCP server.
    """

    agent_name: str
    agent_prompt: str
    mcp_command: str
    mcp_args: list[str] = field(default_factory=list)


def check_kiro_installed() -> bool:
    """Check if Kiro CLI is installed.

    Returns:
        True if kiro-cli is found in PATH, False otherwise.
    """
    return shutil.which("kiro-cli") is not None or shutil.which("kiro") is not None


# Global flag indicating Kiro availability (evaluated at import time)
KIRO_AVAILABLE = check_kiro_installed()


def generate_mcp_config(config: KiroConfig) -> dict[str, Any]:
    """Generate MCP server configuration for Kiro.

    Args:
        config: Kiro configuration.

    Returns:
        Dictionary for mcp.json configuration.
    """
    server_config: dict[str, Any] = {
        "command": "uvx",
        "args": [config.mcp_command] + config.mcp_args,
    }

    return {
        "mcpServers": {
            config.mcp_command: server_config,
        }
    }


def generate_agent_config(config: KiroConfig) -> dict[str, Any]:
    """Generate custom agent configuration for Kiro.

    Args:
        config: Kiro configuration.

    Returns:
        Dictionary for agent.json configuration.
    """
    return {
        "name": config.agent_name,
        "systemPrompt": config.agent_prompt,
        "mcpServers": [config.mcp_command],
    }


def install_configs(
    config: KiroConfig,
    project_dir: Path | None = None,
    home_dir: Path | None = None,
) -> tuple[Path, Path]:
    """Install Kiro configuration files.

    Args:
        config: Kiro configuration.
        project_dir: Project directory for MCP config (default: current directory).
        home_dir: Home directory for agent config (default: user home).

    Returns:
        Tuple of (mcp_config_path, agent_config_path).
    """
    if project_dir is None:
        project_dir = Path.cwd()
    if home_dir is None:
        home_dir = Path.home()

    # Create MCP config in project
    mcp_dir = project_dir / ".kiro"
    mcp_dir.mkdir(parents=True, exist_ok=True)
    mcp_config_path = mcp_dir / "mcp.json"

    mcp_config = generate_mcp_config(config)
    mcp_config_path.write_text(json.dumps(mcp_config, indent=2))

    # Create agent config in home directory
    agents_dir = home_dir / ".kiro" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    agent_config_path = agents_dir / f"{config.agent_name}.json"

    agent_config = generate_agent_config(config)
    agent_config_path.write_text(json.dumps(agent_config, indent=2))

    return mcp_config_path, agent_config_path


def build_kiro_command(
    agent_name: str,
    prompt: str,
    non_interactive: bool = False,
) -> list[str]:
    """Build the kiro-cli command.

    Args:
        agent_name: Name of the custom agent.
        prompt: Initial prompt for the conversation.
        non_interactive: If True, run in non-interactive mode.

    Returns:
        List of command arguments.
    """
    cmd = ["kiro-cli", "chat", "--agent", agent_name]

    if non_interactive:
        cmd.append("--non-interactive")

    cmd.extend(["--prompt", prompt])

    return cmd


def launch_kiro(
    config: KiroConfig,
    prompt: str,
    project_dir: Path | None = None,
    non_interactive: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Launch Kiro CLI with the given configuration.

    Args:
        config: Kiro configuration.
        prompt: Initial prompt for the conversation.
        project_dir: Project directory (default: current directory).
        non_interactive: If True, run in non-interactive mode.

    Returns:
        CompletedProcess result from subprocess.
    """
    if project_dir is None:
        project_dir = Path.cwd()

    # Ensure configs are installed
    install_configs(config, project_dir=project_dir)

    # Build and run command
    cmd = build_kiro_command(
        agent_name=config.agent_name,
        prompt=prompt,
        non_interactive=non_interactive,
    )

    return subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)


__all__ = [
    "KiroConfig",
    "KIRO_AVAILABLE",
    "check_kiro_installed",
    "generate_mcp_config",
    "generate_agent_config",
    "install_configs",
    "build_kiro_command",
    "launch_kiro",
]
