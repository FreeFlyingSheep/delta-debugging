"""Tree-sitter parser for programming languages."""

import logging
from typing import cast, get_args

from tree_sitter import Tree as TSTree
from tree_sitter import Node as TSNode
from tree_sitter import Parser as TSParser
from tree_sitter_language_pack import SupportedLanguage, get_parser

from delta_debugging.input import Input
from delta_debugging.parser import Node, Parser


logger: logging.Logger = logging.getLogger(__name__)


class TreeSitterParser(Parser):
    """Tree-sitter parser."""

    language: SupportedLanguage
    """Supported programming language to parse."""
    parser: TSParser
    """Tree-sitter parser instance."""

    def __init__(self, language: str, *, expand_whitespace: bool = True) -> None:
        """Initialize the Tree-sitter parser.

        Args:
            language: The programming language to parse (e.g. "python").
            expand_whitespace: Whether to expand whitespace in the input.

        Raises:
            ValueError: If the specified language is not supported.

        """
        language = language.lower().strip()
        if language not in get_args(SupportedLanguage):
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported languages are: {', '.join(get_args(SupportedLanguage))}"
            )

        super().__init__(expand_whitespace=expand_whitespace)
        self.language = cast(SupportedLanguage, language)
        self.parser = get_parser(self.language)

    def _parse(self, node: TSNode, depth: int) -> Node:
        """Parse a Tree-sitter node recursively.

        Args:
            node: The Tree-sitter node to parse.
            depth: The depth of the node in the tree.

        Returns:
            The parsed Node.

        """
        logger.debug(f"Parsing Tree-sitter node {node.type} at depth {depth}")

        n: Node = Node(node.type, node.start_byte, node.end_byte, depth)
        n.children = [self._parse(child, depth + 1) for child in node.children]
        return n

    def parse(self, input: Input) -> Node:
        """Parse the input into a tree of nodes.

        Args:
            input: The input to parse.

        Returns:
            The root node of the parsed tree.

        """
        logger.debug(f"Parsing input of length {len(input)} as {self.language}")

        tree: TSTree = self.parser.parse(input.data_type(input.data))
        return self._parse(tree.root_node, 0)

    def __str__(self) -> str:
        """Get a string representation of the parser.

        Returns:
            String representation of the parser.

        """
        return f"TreeSitterParser for {self.language} (expand_whitespace={self.expand_whitespace})"
