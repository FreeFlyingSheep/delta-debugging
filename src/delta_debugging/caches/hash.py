"""Hash-based cache for delta debugging."""

import logging
from typing import Generator

from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.input import Input
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


class HashCache(Cache):
    """Hash-based cache.

    Examples:
        >>> from delta_debugging import Configuration, HashCache, Input, Outcome
        >>> cache = HashCache()
        >>> input = Input([1, 2, 3])
        >>> config = Configuration.from_input(input)
        >>> cache[config] = Outcome.FAIL
        >>> cache[config]
        <Outcome.FAIL: 'fail'>
        >>> config in cache
        True

    """

    _data: dict[Configuration, Outcome]
    """Cache data."""
    _input: Input | None

    def __init__(self) -> None:
        """Initialize the hash-based cache."""
        self._data = {}
        self._input = None

    def __getitem__(self, key: Configuration) -> Outcome:
        """Get the cached outcome for the given configuration.

        Args:
            key: Configuration to look up.

        Returns:
            Cached outcome.

        Raises:
            KeyError: If the configuration is not in the cache.
            ValueError: If the configuration input does not match cache input.

        """
        logger.debug(f"Cache lookup for configuration: {key}")

        if self._input is None:
            raise KeyError(f"{key} not found")
        elif self._input != key.input:
            raise ValueError("Configuration input does not match cache input")

        if key not in self._data:
            raise KeyError(f"{key} not found")
        return self._data[key]

    def __setitem__(self, key: Configuration, value: Outcome) -> None:
        """Set the cached outcome for the given configuration.

        Args:
            key: Configuration to cache.
            value: Outcome to cache.

        Raises:
            ValueError: If the configuration input does not match cache input.

        """
        logger.debug(f"Caching outcome {value} for configuration: {key}")

        if self._input is None:
            self._input = key.input
        elif self._input != key.input:
            raise ValueError("Configuration input does not match cache input")

        self._data[key] = value

    def __contains__(self, key: object) -> bool:
        """Check if the configuration is in the cache.

        Args:
            key: Configuration to check.

        Returns:
            True if the configuration is in the cache, False otherwise.

        Raises:
            ValueError: If the configuration input does not match cache input.

        """
        logger.debug(f"Cache contains check for configuration: {key}")

        if not isinstance(key, Configuration) or self._input is None:
            return False
        elif self._input != key.input:
            raise ValueError("Configuration input does not match cache input")

        return key in self._data

    def __delitem__(self, key: object) -> None:
        """Delete the cached outcome for the given configuration.

        Args:
            key: Configuration to delete.

        Raises:
            KeyError: If the configuration is not in the cache.
            ValueError: If the configuration input does not match cache input.

        """
        logger.debug(f"Deleting cache entry for configuration: {key}")

        if not isinstance(key, Configuration) or self._input is None:
            raise KeyError(f"{key} not found")
        elif self._input != key.input:
            raise ValueError("Configuration input does not match cache input")

        if key not in self._data:
            raise KeyError(f"{key} not found")
        del self._data[key]

    def __iter__(self) -> Generator[Configuration, None, None]:
        """Iterate over the configurations in the cache."""
        yield from self._data.keys()

    def __len__(self) -> int:
        """Get the number of configurations in the cache."""
        return len(self._data)

    def clear(self) -> None:
        """Clear the cache."""
        logger.debug("Clearing cache")

        self._input = None
        self._data.clear()

    def to_string(self) -> str:
        """Get a string representation of the cache."""
        output: list[str] = ["HashCache contents:"]
        for k, v in self._data.items():
            output.append(f"{k}: {v}")
        return "\n".join(output)
