"""Tests for CLI utility functions."""

from pathlib import Path

import pytest

from wetwire_core.cli import (
    error_exit,
    require_optional_dependency,
    resolve_output_dir,
    validate_package_path,
)


class TestErrorExit:
    """Tests for error_exit function."""

    def test_error_exit_default_code(self, capsys):
        """Test error_exit with default exit code."""
        with pytest.raises(SystemExit) as exc_info:
            error_exit("Something went wrong")
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Something went wrong" in captured.err

    def test_error_exit_custom_code(self, capsys):
        """Test error_exit with custom exit code."""
        with pytest.raises(SystemExit) as exc_info:
            error_exit("Custom error", code=42)
        assert exc_info.value.code == 42
        captured = capsys.readouterr()
        assert "Custom error" in captured.err

    def test_error_exit_zero_code(self, capsys):
        """Test error_exit with zero exit code."""
        with pytest.raises(SystemExit) as exc_info:
            error_exit("Info message", code=0)
        assert exc_info.value.code == 0


class TestValidatePackagePath:
    """Tests for validate_package_path function."""

    def test_validate_existing_directory(self, tmp_path):
        """Test validation of existing directory."""
        result = validate_package_path(tmp_path)
        assert result == tmp_path
        assert result.is_dir()

    def test_validate_nonexistent_path(self, tmp_path):
        """Test validation fails for nonexistent path."""
        nonexistent = tmp_path / "does_not_exist"
        with pytest.raises(SystemExit) as exc_info:
            validate_package_path(nonexistent)
        assert exc_info.value.code == 1

    def test_validate_file_not_directory(self, tmp_path):
        """Test validation fails when path is a file, not directory."""
        file_path = tmp_path / "somefile.txt"
        file_path.write_text("content")
        with pytest.raises(SystemExit) as exc_info:
            validate_package_path(file_path)
        assert exc_info.value.code == 1

    def test_validate_resolves_relative_path(self, tmp_path, monkeypatch):
        """Test that relative paths are resolved to absolute."""
        monkeypatch.chdir(tmp_path)
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        result = validate_package_path(Path("subdir"))
        assert result.is_absolute()
        assert result == subdir


class TestResolveOutputDir:
    """Tests for resolve_output_dir function."""

    def test_resolve_none_returns_cwd(self, tmp_path, monkeypatch):
        """Test that None returns current working directory."""
        monkeypatch.chdir(tmp_path)
        result = resolve_output_dir(None)
        assert result == tmp_path

    def test_resolve_existing_directory(self, tmp_path):
        """Test resolution of existing directory."""
        result = resolve_output_dir(tmp_path)
        assert result == tmp_path

    def test_resolve_creates_directory(self, tmp_path):
        """Test that nonexistent directory is created."""
        new_dir = tmp_path / "new_output"
        assert not new_dir.exists()
        result = resolve_output_dir(new_dir)
        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_resolve_nested_directory(self, tmp_path):
        """Test creation of nested directories."""
        nested = tmp_path / "a" / "b" / "c"
        assert not nested.exists()
        result = resolve_output_dir(nested)
        assert result == nested
        assert nested.exists()

    def test_resolve_returns_absolute_path(self, tmp_path, monkeypatch):
        """Test that result is always absolute."""
        monkeypatch.chdir(tmp_path)
        result = resolve_output_dir(Path("relative_dir"))
        assert result.is_absolute()


class TestRequireOptionalDependency:
    """Tests for require_optional_dependency function."""

    def test_require_installed_dependency(self):
        """Test that installed dependency returns successfully."""
        # pytest is installed in dev environment
        require_optional_dependency("pytest")

    def test_require_missing_dependency(self):
        """Test that missing dependency exits with error."""
        with pytest.raises(SystemExit) as exc_info:
            require_optional_dependency("nonexistent_package_xyz_123")
        assert exc_info.value.code == 1

    def test_require_dependency_with_install_hint(self, capsys):
        """Test that error message includes install hint."""
        with pytest.raises(SystemExit):
            require_optional_dependency("fake_package")
        captured = capsys.readouterr()
        assert "fake_package" in captured.err
        assert "pip install" in captured.err.lower() or "install" in captured.err.lower()
