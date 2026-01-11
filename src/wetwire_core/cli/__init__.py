"""CLI utility functions for wetwire domain packages."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def error_exit(message: str, code: int = 1) -> None:
    """Print error message to stderr and exit with specified code.

    Args:
        message: Error message to display.
        code: Exit code (default: 1).
    """
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)


def validate_package_path(path: Path) -> Path:
    """Validate that path exists and is a directory.

    Args:
        path: Path to validate.

    Returns:
        Resolved absolute path.

    Raises:
        SystemExit: If path doesn't exist or is not a directory.
    """
    resolved = path.resolve()
    if not resolved.exists():
        error_exit(f"Path does not exist: {resolved}")
    if not resolved.is_dir():
        error_exit(f"Path is not a directory: {resolved}")
    return resolved


def resolve_output_dir(path: Path | None) -> Path:
    """Resolve output directory, creating it if necessary.

    Args:
        path: Output directory path, or None for current directory.

    Returns:
        Resolved absolute path to output directory.
    """
    if path is None:
        return Path.cwd()

    resolved = path.resolve()
    if not resolved.exists():
        resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def require_optional_dependency(name: str) -> None:
    """Check that an optional dependency is installed.

    Args:
        name: Name of the package to check.

    Raises:
        SystemExit: If package is not installed.
    """
    spec = importlib.util.find_spec(name)
    if spec is None:
        error_exit(
            f"Required dependency '{name}' is not installed. Install it with: pip install {name}"
        )


__all__ = [
    "error_exit",
    "validate_package_path",
    "resolve_output_dir",
    "require_optional_dependency",
]
