"""Tests for provider abstraction layer."""

from unittest.mock import MagicMock

import pytest


class TestProviderProtocol:
    """Tests for Provider protocol."""

    def test_provider_protocol_exists(self):
        """Test that Provider protocol is defined."""
        from wetwire_core.providers import Provider

        assert Provider is not None

    def test_provider_has_create_message_method(self):
        """Test that Provider has create_message method signature."""
        from wetwire_core.providers import Provider

        # Protocol should define create_message
        assert hasattr(Provider, "create_message")

    def test_provider_has_stream_message_method(self):
        """Test that Provider has stream_message method signature."""
        from wetwire_core.providers import Provider

        # Protocol should define stream_message
        assert hasattr(Provider, "stream_message")


class TestAnthropicProvider:
    """Tests for AnthropicProvider implementation."""

    def test_anthropic_provider_exists(self):
        """Test that AnthropicProvider is defined."""
        from wetwire_core.providers import AnthropicProvider

        assert AnthropicProvider is not None

    def test_anthropic_provider_implements_protocol(self):
        """Test that AnthropicProvider implements Provider protocol."""
        from wetwire_core.providers import AnthropicProvider

        # Should have the required methods
        provider = AnthropicProvider()
        assert hasattr(provider, "create_message")
        assert hasattr(provider, "stream_message")
        assert callable(provider.create_message)
        assert callable(provider.stream_message)

    def test_anthropic_provider_default_model(self):
        """Test AnthropicProvider has default model."""
        from wetwire_core.providers import AnthropicProvider

        provider = AnthropicProvider()
        assert hasattr(provider, "model")
        assert "claude" in provider.model.lower()

    def test_anthropic_provider_custom_model(self):
        """Test AnthropicProvider accepts custom model."""
        from wetwire_core.providers import AnthropicProvider

        provider = AnthropicProvider(model="claude-3-haiku-20240307")
        assert provider.model == "claude-3-haiku-20240307"

    def test_create_message_calls_anthropic_api(self):
        """Test that create_message calls the Anthropic API."""
        from wetwire_core.providers import AnthropicProvider

        # Setup mock client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "Hello"
        mock_response.content = [mock_block]
        mock_response.stop_reason = "end_turn"
        mock_response.model = "claude-sonnet-4-20250514"
        mock_response.usage = MagicMock(input_tokens=10, output_tokens=5)
        mock_client.messages.create.return_value = mock_response

        # Create provider with mocked client
        provider = AnthropicProvider(client=mock_client)
        result = provider.create_message(
            messages=[{"role": "user", "content": "Hello"}],
            system="You are helpful.",
            max_tokens=100,
        )

        mock_client.messages.create.assert_called_once()
        assert result["stop_reason"] == "end_turn"

    def test_stream_message_returns_iterator(self):
        """Test that stream_message returns an iterator."""
        from wetwire_core.providers import AnthropicProvider

        # Setup mock client
        mock_client = MagicMock()
        mock_stream = MagicMock()
        mock_stream.__iter__ = MagicMock(return_value=iter([]))
        mock_client.messages.stream.return_value.__enter__ = MagicMock(return_value=mock_stream)
        mock_client.messages.stream.return_value.__exit__ = MagicMock(return_value=None)

        # Create provider with mocked client
        provider = AnthropicProvider(client=mock_client)
        result = provider.stream_message(
            messages=[{"role": "user", "content": "Hello"}],
            system="You are helpful.",
            max_tokens=100,
        )

        # Should return an iterator
        assert hasattr(result, "__iter__")


class TestGetProvider:
    """Tests for get_provider factory function."""

    def test_get_provider_anthropic(self):
        """Test getting Anthropic provider."""
        from wetwire_core.providers import AnthropicProvider, get_provider

        provider = get_provider("anthropic")
        assert isinstance(provider, AnthropicProvider)

    def test_get_provider_invalid_raises_error(self):
        """Test that invalid provider name raises ValueError."""
        from wetwire_core.providers import get_provider

        with pytest.raises(ValueError) as exc_info:
            get_provider("invalid_provider")
        assert "Unknown provider" in str(exc_info.value)

    def test_get_provider_with_model(self):
        """Test getting provider with custom model."""
        from wetwire_core.providers import get_provider

        provider = get_provider("anthropic", model="claude-3-haiku-20240307")
        assert provider.model == "claude-3-haiku-20240307"
