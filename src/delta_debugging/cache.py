"""Abstract cache class for delta debugging."""

import logging
from abc import abstractmethod
from collections.abc import MutableMapping
from typing import Generator

from delta_debugging.configuration import Configuration
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


class Cache(MutableMapping[Configuration, Outcome]):
    """Abstract cache class."""

    @abstractmethod
    def __str__(self) -> str:
        """Get a string representation of the cache."""
        pass

    @abstractmethod
    def __getitem__(self, key: Configuration) -> Outcome:
        """Get the outcome for the given configuration.

        Args:
            key: Configuration to look up.

        """
        pass

    @abstractmethod
    def __setitem__(self, key: Configuration, value: Outcome) -> None:
        """Set the outcome for the given configuration.

        Args:
            key: Configuration to cache.
            value: Outcome to cache.

        """
        pass

    @abstractmethod
    def __contains__(self, key: object) -> bool:
        """Check if the cache contains the given configuration.

        Args:
            key: Configuration to check.

        """
        pass

    @abstractmethod
    def __delitem__(self, key: object) -> None:
        """Delete the outcome for the given configuration.

        Args:
            key: Configuration to delete.

        """
        pass

    @abstractmethod
    def __iter__(self) -> Generator[Configuration, None, None]:
        """Iterate over the configurations in the cache."""
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Get the number of configurations in the cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the cache."""
        pass

    @abstractmethod
    def to_string(self) -> str:
        """Get a string representation of the cache."""
        pass
