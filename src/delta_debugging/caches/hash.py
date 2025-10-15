"""Hash-based cache for delta debugging."""

import logging
from typing import Any, Generator

from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


class HashCache(Cache):
    """Hash-based cache.

    Examples:
        >>> from delta_debugging import Configuration, HashCache, Outcome
        >>> cache = HashCache()
        >>> config = [1, 2, 3]
        >>> cache[config] = Outcome.FAIL
        >>> cache[config]
        <Outcome.FAIL: 'fail'>
        >>> config in cache
        True
        >>> print(cache)
        Hash Cache

    """

    _data: dict[tuple[Any], Outcome]
    """Cache data."""

    def __init__(self) -> None:
        """Initialize the hash-based cache."""
        self._data = {}

    def __str__(self) -> str:
        """Get a string representation of the cache."""
        return "Hash Cache"

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

        tuple_key: tuple[Any] = tuple(key)
        if tuple_key not in self._data:
            raise KeyError(f"{key} not found")
        return self._data[tuple_key]

    def __setitem__(self, key: Configuration, value: Outcome) -> None:
        """Set the cached outcome for the given configuration.

        Args:
            key: Configuration to cache.
            value: Outcome to cache.

        """
        logger.debug(f"Caching outcome {value} for configuration: {key}")

        self._data[tuple(key)] = value

    def __contains__(self, key: object) -> bool:
        """Check if the configuration is in the cache.

        Args:
            key: Configuration to check.

        Returns:
            True if the configuration is in the cache, False otherwise.

        """
        logger.debug(f"Cache contains check for configuration: {key}")

        if not isinstance(key, list):
            return False

        return tuple(key) in self._data

    def __delitem__(self, key: object) -> None:
        """Delete the cached outcome for the given configuration.

        Args:
            key: Configuration to delete.

        Raises:
            KeyError: If the configuration is not in the cache.

        """
        logger.debug(f"Deleting cache entry for configuration: {key}")

        if not isinstance(key, list):
            raise KeyError(f"{key} not found")

        tuple_key: tuple[Any] = tuple(key)
        if tuple_key not in self._data:
            raise KeyError(f"{tuple_key} not found")
        del self._data[tuple_key]

    def __iter__(self) -> Generator[Configuration, None, None]:
        """Iterate over the configurations in the cache."""
        yield from [list(key) for key in self._data.keys()]

    def __len__(self) -> int:
        """Get the number of configurations in the cache."""
        return len(self._data)

    def clear(self) -> None:
        """Clear the cache."""
        logger.debug("Clearing cache")

        self._data.clear()

    def to_string(self) -> str:
        """Get a string representation of the cache."""
        output: list[str] = ["HashCache contents:"]
        for k, v in self._data.items():
            output.append(f"{k}: {v}")
        return "\n".join(output)
