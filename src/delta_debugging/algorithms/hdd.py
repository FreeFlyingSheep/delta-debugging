"""Hierarchical Delta Debugging (HDD) delta debugging algorithm."""

import logging
from typing import Callable

from delta_debugging.algorithm import Algorithm
from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration

from delta_debugging.outcome import Outcome
from delta_debugging.parser import Node, Parser


logger: logging.Logger = logging.getLogger(__name__)


class _Tree:
    """HDD tree."""

    config: Configuration
    """Original configuration."""
    expand_whitespace: bool
    """Whether to expand whitespace."""
    depth: int
    """The depth of the tree."""
    root: Node
    """The root node of the tree."""

    def __init__(
        self, root: Node, config: Configuration, expand_whitespace: bool
    ) -> None:
        """Initialize the HDD tree.

        Args:
            root: Root node of the tree.
            config: Configuration to reduce.
            expand_whitespace: Whether to expand whitespace.

        """
        self.config = config
        self.expand_whitespace = expand_whitespace
        self.depth = 0
        self.root = self._parse(root, 0)

    def _parse(self, node: Node, depth: int) -> Node:
        """Parse a node and its children.

        Args:
            node: Node to parse.
            depth: Depth of the node.

        Returns:
            Root node of the parsed tree.

        """
        while len(node.children) == 1:
            node = node.children[0]

        self.depth = max(self.depth, depth)

        n: Node = Node(node.name, node.start, node.end, depth)
        n.children = [self._parse(child, depth + 1) for child in node.children]
        return n

    def _expand(self, node: Node) -> Configuration:
        """Expand the whitespace in the given node.

        Args:
            node: Node to expand.

        Returns:
            Configuration with expanded whitespace.

        """
        for i in range(node.end + 1, min(node.end + 4, len(self.config) + 1)):
            if bytes(self.config[node.end : i]).isspace():
                return self.config[node.end : i]
        return []

    def _unparse(self, node: Node) -> Configuration:
        """Unparse the given node.

        Args:
            node: Node to unparse.

        Returns:
            Configuration representing the node.

        """
        if not node.exists:
            return []

        if not node.children:
            config = self.config[node.start : node.end]
            if self.expand_whitespace:
                config += self._expand(node)
            return config

        config: Configuration = []
        for child in node.children:
            if child.exists:
                config += self._unparse(child)
        return config

    def subsets(self, node: Node) -> list[Configuration]:
        """Get all subsets of the given node.

        Args:
            node: Node to get subsets from.

        Returns:
            List of all subsets of the node.

        """
        configs: list[Configuration] = []
        for child in node.children:
            if not child.exists:
                continue

            config: Configuration = self.config[child.start : child.end]
            if self.expand_whitespace:
                config += self._expand(child)
            configs.append(config)
        return configs

    def unparse(self) -> Configuration:
        """Unparse the tree.

        Returns:
            Configuration representing the tree.

        """
        return self._unparse(self.root)

    def nodes(self, level: int) -> list[Node]:
        """Get all nodes at the given level.

        Args:
            level: Level to get nodes from.

        Returns:
            List of nodes at the given level.

        """
        depth = 0
        nodes: list[Node] = [self.root]
        while depth < level:
            queue: list[Node] = []
            for node in nodes:
                if not node.exists:
                    continue
                for child in node.children:
                    if child.exists:
                        queue.append(child)
            nodes = queue
            depth += 1
        return nodes

    def prune(self, node: Node, config: Configuration) -> None:
        """Prune the node based on the configuration.

        Args:
            node: Node to prune.
            config: Configuration to use for pruning.

        """
        if self.expand_whitespace:
            contents: list[bytes] = [bytes(c).strip() for c in config]
        else:
            contents = [bytes(c) for c in config]
        for child in node.children:
            if not child.exists:
                continue
            if self.expand_whitespace:
                content: bytes = bytes(self.config[child.start : child.end]).strip()
            else:
                content = bytes(self.config[child.start : child.end])
            if content not in contents:
                child.exists = False


class HDD(Algorithm):
    """HDD algorithm.

    Examples:
        >>> from delta_debugging import DDMin, HDD, TreeSitterParser
        >>> str(HDD(TreeSitterParser("python", expand_whitespace=True), DDMin()))
        'HDD with ddmin using TreeSitterParser for python (expand_whitespace=True)'

    """

    parser: Parser
    """Parser to use for parsing the input."""
    algorithm: Algorithm
    """Algorithm to use for minimizing subsets."""

    def __init__(self, parser: Parser, algorithm: Algorithm) -> None:
        """Initialize the HDD algorithm.

        Args:
            parser: Parser to use for parsing the input.
            algorithm: Algorithm to use for minimizing subsets.

        """
        self.parser = parser
        self.algorithm = algorithm

    def __str__(self) -> str:
        """Get the string representation of the DDMin algorithm.

        Returns:
            Name of the algorithm.

        """
        return f"HDD with {self.algorithm} using {self.parser}"

    def _oracle(
        self,
        oracle: Callable[[Configuration], Outcome],
    ) -> Callable[[Configuration], Outcome]:
        """Wrap the oracle function to convert configurations of lists to flat configurations.

        Args:
            oracle: Oracle function to wrap.

        Returns:
            Wrapped oracle function.

        """

        def _wrapper(config: Configuration) -> Outcome:
            """Convert configurations of lists to flat configurations.

            Args:
                config (Configuration): Configuration to convert.

            Returns:
                Outcome: Result of the oracle function.

            """
            conf: Configuration = []
            for c in config:
                conf += c
            return oracle(conf)

        return _wrapper

    def run(
        self,
        config: Configuration,
        oracle: Callable[[Configuration], Outcome],
        *,
        cache: Cache | None = None,
    ) -> Configuration:
        """Run the HDD algorithm.

        Args:
            config: Configuration to reduce.
            oracle: The oracle function.
            cache: Cache for storing test outcomes.

        Returns:
            The reduced configuration.

        """
        logger.debug("Starting HDD algorithm")
        root: Node = self.parser.parse(config)
        tree: _Tree = _Tree(root, config, self.parser.expand_whitespace)

        level: int = 0
        while True:
            nodes: list[Node] = tree.nodes(level)
            if not nodes:
                break

            for node in nodes:
                configs: list[Configuration] = tree.subsets(node)

                if len(configs) <= 1:
                    continue

                if cache is not None:
                    cache.clear()

                c: Configuration = self.algorithm.run(
                    configs, self._oracle(oracle), cache=cache
                )
                logger.debug(
                    f"Testing node at level {level} with {len(configs)} subsets: "
                    f"{configs} => {c}"
                )
                tree.prune(node, c)
                logger.debug(f"Pruned tree at level {level}: {tree.unparse()}")

            level += 1

        config = tree.unparse()
        logger.debug(f"HDD algorithm completed with reduced configuration: {config}")
        return config
