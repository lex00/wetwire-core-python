"""Provider abstraction layer for multi-backend AI support.

This module provides a unified interface for different AI providers:
- Anthropic (Claude API)
- Kiro (AWS-based AI)

Usage:
    from wetwire_core.providers import get_provider, AnthropicProvider

    # Get default provider
    provider = get_provider("anthropic")

    # Use provider
    response = provider.create_message(
        messages=[{"role": "user", "content": "Hello"}],
        system="You are helpful.",
    )
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

import anthropic


@runtime_checkable
class Provider(Protocol):
    """Protocol for AI provider implementations.

    All providers must implement create_message and stream_message methods.
    """

    model: str

    def create_message(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Create a message using the provider's API.

        Args:
            messages: Conversation history.
            system: System prompt.
            tools: Optional list of tool definitions.
            max_tokens: Maximum tokens in response.

        Returns:
            Response dictionary with content and metadata.
        """
        ...

    def stream_message(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 4096,
    ) -> Iterator[dict[str, Any]]:
        """Stream a message response from the provider.

        Args:
            messages: Conversation history.
            system: System prompt.
            tools: Optional list of tool definitions.
            max_tokens: Maximum tokens in response.

        Yields:
            Stream events from the provider.
        """
        ...


@dataclass
class AnthropicProvider:
    """Anthropic Claude API provider.

    Wraps the Anthropic SDK to provide a consistent interface.
    """

    model: str = "claude-sonnet-4-20250514"
    client: anthropic.Anthropic = field(default_factory=anthropic.Anthropic)

    def create_message(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Create a message using Claude API.

        Args:
            messages: Conversation history.
            system: System prompt.
            tools: Optional list of tool definitions.
            max_tokens: Maximum tokens in response.

        Returns:
            Response dictionary with content and metadata.
        """
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = self.client.messages.create(**kwargs)

        # Convert response to dict format
        return {
            "content": [
                {"type": block.type, "text": getattr(block, "text", None)}
                if block.type == "text"
                else {
                    "type": block.type,
                    "id": getattr(block, "id", None),
                    "name": getattr(block, "name", None),
                    "input": getattr(block, "input", None),
                }
                for block in response.content
            ],
            "stop_reason": response.stop_reason,
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }

    def stream_message(
        self,
        messages: list[dict[str, Any]],
        system: str,
        tools: list[dict[str, Any]] | None = None,
        max_tokens: int = 4096,
    ) -> Iterator[dict[str, Any]]:
        """Stream a message response from Claude API.

        Args:
            messages: Conversation history.
            system: System prompt.
            tools: Optional list of tool definitions.
            max_tokens: Maximum tokens in response.

        Yields:
            Stream events from Claude API.
        """
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        with self.client.messages.stream(**kwargs) as stream:
            for event in stream:
                yield {"type": event.type, "event": event}


def get_provider(name: str, model: str | None = None) -> Provider:
    """Get a provider instance by name.

    Args:
        name: Provider name ("anthropic", "kiro").
        model: Optional model override.

    Returns:
        Provider instance.

    Raises:
        ValueError: If provider name is not recognized.
    """
    providers = {
        "anthropic": AnthropicProvider,
    }

    if name not in providers:
        valid = ", ".join(providers.keys())
        raise ValueError(f"Unknown provider '{name}'. Valid: {valid}")

    provider_cls = providers[name]
    if model:
        return provider_cls(model=model)
    return provider_cls()


__all__ = [
    "Provider",
    "AnthropicProvider",
    "get_provider",
]
