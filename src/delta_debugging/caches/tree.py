"""Tree-based cache for delta debugging."""

import logging
from typing import Generator
from dataclasses import dataclass, field

from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.input import Input
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class _Node:
    """Node in the tree cache."""

    value: Outcome | None = None
    """Cached outcome."""
    children: dict[int, "_Node"] = field(default_factory=dict)
    """Children nodes."""


class TreeCache(Cache):
    """Tree-based cache.

    Examples:
        >>> from delta_debugging import Configuration, Input, Outcome, TreeCache
        >>> cache = TreeCache()
        >>> input = Input([1, 2, 3])
        >>> config = Configuration.from_input(input)
        >>> cache[config] = Outcome.FAIL
        >>> cache[config]
        <Outcome.FAIL: 'fail'>
        >>> config in cache
        True
        >>> print(cache)
        Tree Cache

    """

    _root: _Node
    """Root node of the tree."""
    _length: int = 0
    """Number of configurations in the cache."""
    _input: Input | None
    """Input associated with the cache."""

    def __init__(self) -> None:
        """Initialize the tree-based cache."""
        self._root = _Node()
        self._length = 0
        self._input = None

    def __str__(self) -> str:
        """Get a string representation of the cache."""
        return "Tree Cache"

    def __getitem__(self, key: Configuration) -> Outcome:
        """Get the cached outcome for the given configuration.

        Args:
            key: Configuration to look up.

        Returns:
            Cached outcome.

        Raises:
            KeyError: If the configuration is not in the cache.

        """
        logger.debug(f"Cache lookup for configuration: {key}")

        if self._input is None:
            raise KeyError(f"{key} not found")
        elif self._input != key.input:
            raise ValueError("Configuration input does not match cache input")

        node: _Node = self._root
        for c in key:
            if c not in node.children:
                raise KeyError(f"{key} not found")
            node = node.children[c]
        if node.value is None:
            raise KeyError(f"{key} not found")
        return node.value

    def __setitem__(self, key: Configuration, value: Outcome) -> None:
        """Set the cached outcome for the given configuration.

        Args:
            key: Configuration to cache.
            value: Outcome to cache.

        Raises:
            ValueError: If the configuration input does not match the cache input.

        """
        logger.debug(f"Caching outcome {value} for configuration: {key}")

        if self._input is None:
            self._input = key.input
        elif self._input != key.input:
            raise ValueError("Configuration input does not match cache input")

        node: _Node = self._root
        for c in key:
            if c not in node.children:
                node.children[c] = _Node()
                self._length += 1
            node = node.children[c]
        node.value = value

        if value is Outcome.FAIL:
            queue: list[tuple[_Node, int]] = [(node, len(key))]
            while queue:
                node, length = queue.pop()
                if length == 0:
                    node.children = {}
                else:
                    for n in node.children.values():
                        queue.append((n, length - 1))

    def __contains__(self, key: object) -> bool:
        """Check if the cache contains the given configuration.

        Args:
            key: Configuration to check.

        Returns:
            True if the configuration is in the cache, False otherwise.

        Raises:
            ValueError: If the configuration input does not match the cache input.

        """
        logger.debug(f"Cache contains check for configuration: {key}")

        if not isinstance(key, Configuration) or self._input is None:
            return False
        elif self._input != key.input:
            raise ValueError("Configuration input does not match cache input")

        node: _Node = self._root
        for c in key:
            if c not in node.children:
                return False
            node = node.children[c]
        return node.value is not None

    def __delitem__(self, key: object) -> None:
        """Delete the cached outcome for the given configuration.

        Args:
            key: Configuration to delete.

        Raises:
            KeyError: If the configuration is not in the cache.
            ValueError: If the configuration input does not match the cache input.

        """
        logger.debug(f"Deleting cache entry for configuration: {key}")

        if not isinstance(key, Configuration) or self._input is None:
            raise KeyError(f"{key} not found")
        elif self._input != key.input:
            raise ValueError("Configuration input does not match cache input")

        node: _Node = self._root
        for c in key:
            if c not in node.children:
                raise KeyError(f"{key} not found")
            node = node.children[c]
        if node.value is None:
            raise KeyError(f"{key} not found")
        node.value = None
        self._length -= 1

    def __iter__(self) -> Generator[Configuration, None, None]:
        """Iterate over the configurations in the cache."""
        if self._input is None:
            return

        queue: list[tuple[list[int], _Node]] = []
        for k, v in self._root.children.items():
            queue.append(([k], v))
        while queue:
            config, node = queue.pop()
            if node.value is not None:
                yield Configuration(self._input, config)
            for k, v in node.children.items():
                queue.append((config + [k], v))

    def __len__(self) -> int:
        """Get the number of configurations in the cache."""
        return self._length

    def clear(self) -> None:
        """Clear the cache."""
        logger.debug("Clearing cache")

        self._input = None
        self._root = _Node()

    def to_string(self) -> str:
        """Get a string representation of the cache."""
        output: list[str] = ["TreeCache contents:"]
        queue: list[tuple[list[int], _Node]] = []
        for k, v in self._root.children.items():
            queue.append(([k], v))
        while queue:
            config, node = queue.pop()
            if node.value is not None:
                output.append(f"{config}: {node.value}")
            for k, v in node.children.items():
                queue.append((config + [k], v))
        return "\n".join(output)
