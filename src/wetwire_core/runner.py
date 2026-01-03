"""Runner message types.

This module provides message types used in the agent conversation system.
"""

from dataclasses import dataclass


@dataclass
class Message:
    """A message in the conversation between Developer and Runner.

    Attributes:
        role: The role of the message sender (developer, runner, system, tool)
        content: The content of the message
    """

    role: str
    content: str
