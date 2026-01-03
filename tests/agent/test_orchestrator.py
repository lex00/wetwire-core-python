"""Tests for agent.orchestrator module."""

import pytest

from wetwire_core.agent.orchestrator import (
    Orchestrator,
    Session,
    SessionConfig,
)


class TestSessionConfig:
    """Tests for SessionConfig dataclass."""

    def test_session_config_creation_minimal(self):
        """Test SessionConfig creation with minimal fields."""
        config = SessionConfig(domain="aws")
        assert config.domain == "aws"
        assert config.max_lint_cycles == 3
        assert config.output_dir is None

    def test_session_config_creation_full(self):
        """Test SessionConfig creation with all fields."""
        config = SessionConfig(
            domain="gcp",
            max_lint_cycles=5,
            output_dir="/tmp/output",
        )
        assert config.domain == "gcp"
        assert config.max_lint_cycles == 5
        assert config.output_dir == "/tmp/output"


class TestSession:
    """Tests for Session dataclass."""

    def test_session_creation_minimal(self):
        """Test Session creation with minimal fields."""
        config = SessionConfig(domain="aws")
        session = Session(config=config)

        assert session.config == config
        assert session.messages == []
        assert session.lint_cycles == 0
        assert session.complete is False
        assert session.score is None

    def test_session_creation_with_data(self):
        """Test Session creation with data."""
        config = SessionConfig(domain="aws")
        messages = [{"role": "user", "content": "Create a VPC"}]
        session = Session(
            config=config,
            messages=messages,
            lint_cycles=2,
            complete=True,
            score=12,
        )

        assert session.config == config
        assert session.messages == messages
        assert session.lint_cycles == 2
        assert session.complete is True
        assert session.score == 12


class TestOrchestrator:
    """Tests for Orchestrator class."""

    def test_orchestrator_initialization(self):
        """Test that Orchestrator can be initialized."""
        orchestrator = Orchestrator()
        assert orchestrator is not None

    def test_create_session_minimal(self):
        """Test create_session with minimal parameters."""

        class MockDeveloper:
            def respond(self, message: str) -> str:
                return "response"

        class MockRunner:
            def process(self, message: str) -> str:
                return "result"

            def is_complete(self) -> bool:
                return False

        orchestrator = Orchestrator()
        developer = MockDeveloper()
        runner = MockRunner()

        session = orchestrator.create_session(
            domain="aws",
            developer=developer,
            runner=runner,
        )

        assert isinstance(session, Session)
        assert session.config.domain == "aws"
        assert session.config.max_lint_cycles == 3
        assert session.messages == []
        assert session.lint_cycles == 0
        assert session.complete is False

    def test_create_session_with_max_lint_cycles(self):
        """Test create_session with custom max_lint_cycles."""

        class MockDeveloper:
            def respond(self, message: str) -> str:
                return "response"

        class MockRunner:
            def process(self, message: str) -> str:
                return "result"

            def is_complete(self) -> bool:
                return False

        orchestrator = Orchestrator()
        developer = MockDeveloper()
        runner = MockRunner()

        session = orchestrator.create_session(
            domain="gcp",
            developer=developer,
            runner=runner,
            max_lint_cycles=5,
        )

        assert session.config.domain == "gcp"
        assert session.config.max_lint_cycles == 5

    def test_run_not_implemented(self):
        """Test that run() raises NotImplementedError."""
        orchestrator = Orchestrator()
        config = SessionConfig(domain="aws")
        session = Session(config=config)

        with pytest.raises(NotImplementedError) as exc_info:
            orchestrator.run(session, "Create infrastructure")

        assert "not yet implemented" in str(exc_info.value).lower()
