"""Tests for runner module."""

from wetwire_core.runner import Message


class TestMessage:
    """Tests for Message dataclass."""

    def test_message_creation(self):
        """Test that Message can be created with role and content."""
        message = Message(role="developer", content="Create a VPC")
        assert message.role == "developer"
        assert message.content == "Create a VPC"

    def test_message_different_roles(self):
        """Test Message with different roles."""
        roles = ["developer", "runner", "system", "tool"]
        for role in roles:
            message = Message(role=role, content="test content")
            assert message.role == role
            assert message.content == "test content"
