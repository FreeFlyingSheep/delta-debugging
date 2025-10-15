"""Node class and abstract parser class for delta debugging."""

import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TextIO

from delta_debugging.configuration import Configuration

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class Node:
    """Node in the hierarchical structure of the input."""

    name: str
    """Name of the node."""
    start: int
    """Start position of the node."""
    end: int
    """End position of the node."""
    depth: int
    """Depth of the node in the tree."""
    exists: bool = True
    """Whether the node exists in the input."""
    children: list["Node"] = field(default_factory=list)
    """Children of the node."""

    def to_string(
        self,
        *,
        show_removed: bool = True,
        show_children: bool = True,
        stream: TextIO = sys.stdout,
    ) -> str:
        """Get a string representation of the node and its children.

        Args:
            show_removed: Whether to show removed nodes. Defaults to True.
            show_children: Whether to show children. Defaults to True.
            stream: Stream to print to. Defaults to sys.stdout.

        Returns:
            String representation of the node and its children.

        """
        if not show_removed and not self.exists:
            return ""
        result = f"{self.depth * '  '}{self.name} (start={self.start}, end={self.end})"
        if show_removed:
            result += f" [{'exists' if self.exists else 'removed'}]"
        result += "\n"
        if show_children:
            for child in self.children:
                result += child.to_string(
                    show_removed=show_removed,
                    show_children=show_children,
                    stream=stream,
                )
        return result


class Parser(ABC):
    """Abstract parser class."""

    def __init__(self, *, expand_whitespace: bool) -> None:
        """Initialize the parser.

        Args:
            expand_whitespace: Whether to expand whitespace nodes.

        """
        self.expand_whitespace: bool = expand_whitespace

    @abstractmethod
    def parse(self, config: Configuration) -> Node:
        """Parse the configuration into a hierarchical structure.

        Args:
            config: configuration to parse.

        Returns:
            Root node of the hierarchical structure.

        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Get a string representation of the parser.

        Returns:
            String representation of the parser.

        """
        pass
