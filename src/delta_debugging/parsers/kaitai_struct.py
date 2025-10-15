"""KaiTai Struct parser for binaries."""

import logging
from typing import cast, get_args, Literal

from delta_debugging.configuration import Configuration
from delta_debugging.parser import Node, Parser
from delta_debugging.parsers.kaitai_structs import parse_elf


logger: logging.Logger = logging.getLogger(__name__)

SupportedBinary = Literal["elf",]
"""Supported binary formats for Kaitai Struct parser."""


class KaitaiStructParser(Parser):
    """Kaitai Struct parser."""

    binary: SupportedBinary
    """Supported binary formats for Kaitai Struct parser."""
    expand_bytes: bool
    """Whether to expand nodes into individual bytes."""

    def __init__(self, binary: str, expand_bytes: bool = True) -> None:
        """Initialize the Kaitai Struct parser.

        Args:
            binary: The binary format to parse (e.g., "elf").
            expand_bytes: Whether to expand nodes into individual bytes.

        Raises:
            ValueError: If the specified binary format is not supported.

        """
        binary = binary.lower().strip()
        if binary not in get_args(SupportedBinary):
            raise ValueError(
                f"Unsupported binary format: {binary}. "
                f"Supported formats are: {', '.join(get_args(SupportedBinary))}"
            )

        super().__init__(expand_whitespace=False)
        self.binary = cast(SupportedBinary, binary)
        self.expand_bytes = expand_bytes

    def _expand_bytes(self, node: Node) -> None:
        """Expand nodes into individual byte nodes.

        Args:
            node: Node to expand.

        """
        logger.debug(f"Expanding bytes for node {node.name}")

        if len(node.children) > 0:
            for child in node.children:
                self._expand_bytes(child)
            return

        if node.end - node.start <= 1:
            return

        for i in range(node.end - node.start):
            child: Node = Node(
                f"Byte[{i}]", node.start + i, node.start + i + 1, node.depth + 1
            )
            node.children.append(child)

    def parse(self, config: Configuration) -> Node:
        """Parse the configuration and return its tree representation.

        Args:
            config: Configuration to parse.

        Returns:
            Root node of the tree representation.

        """
        logger.debug(f"Parsing configuration of length {len(config)} as {self.binary}")

        if self.binary == "elf":
            root: Node = parse_elf(config)
        else:
            raise ValueError(f"Unsupported binary format: {self.binary}")
        if self.expand_bytes:
            self._expand_bytes(root)
        return root

    def __str__(self) -> str:
        """Get a string representation of the parser.

        Returns:
            String representation of the parser.

        """
        return (
            f"KaitaiStructParser for {self.binary} (expand_bytes={self.expand_bytes})"
        )
