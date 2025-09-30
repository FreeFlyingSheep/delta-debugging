"""Configuration for delta debugging."""

import logging
from collections.abc import Sequence
from typing import Any, Iterator, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from delta_debugging.input import Input


logger: logging.Logger = logging.getLogger(__name__)


class Configuration(Sequence):
    """Configuration of an input."""

    input: "Input"
    """The input associated with this configuration."""
    _data: list[int]
    """The indices of the input that are included in this configuration."""

    def __init__(self, input: "Input", indices: Sequence[int]) -> None:
        """Initialize the configuration.

        Args:
            input: The input associated with this configuration.
            indices: The indices of the input that are included in this configuration.

        """
        self.input = input
        self._data = list(indices)

    @classmethod
    def from_input(cls, input: "Input") -> Self:
        """Create a configuration that includes all elements of the input.

        Args:
            input: The input to create the configuration for.

        Returns:
            A configuration that includes all elements of the input.

        """
        return cls(input, range(len(input)))

    @classmethod
    def empty(cls, input: "Input") -> Self:
        """Create an empty configuration for the input.

        Args:
            input: The input to create the configuration for.

        Returns:
            An empty configuration for the input.

        """
        return cls(input, [])

    def __getitem__(self, index: int | slice) -> "Configuration":
        """Get a subset of the configuration.

        Args:
            index: The index or slice to get.

        Returns:
            A new configuration with the specified indices.

        """
        if isinstance(index, slice):
            return self.__class__(self.input, self._data[index])
        else:
            return self.__class__(self.input, [self._data[index]])

    def __contains__(self, key: object) -> bool:
        """Check if the configuration contains the given key.

        Args:
            key: The key to check for.

        Returns:
            True if the key is in the configuration, False otherwise.

        """
        if not isinstance(key, int):
            raise TypeError("Key must be an integer")
        return key in self._data

    def __iter__(self) -> Iterator[Any]:
        """Get an iterator over the configuration.

        Returns:
            An iterator over the configuration.

        """
        return iter(self._data)

    def __len__(self) -> int:
        """Get the length of the configuration.

        Returns:
            The length of the configuration.

        """
        return len(self._data)

    def __add__(self, other: "Configuration") -> "Configuration":
        """Combine two configurations.

        Args:
            other: The other configuration to combine with.

        Returns:
            A new configuration that combines the two configurations.

        """
        if self.input != other.input:
            raise ValueError("Input does not match")
        return self.__class__(self.input, sorted(self._data + other._data))

    def __sub__(self, other: "Configuration") -> "Configuration":
        """Get the difference between two configurations.

        Args:
            other: The other configuration to subtract.

        Returns:
            A new configuration that is the difference between the two configurations.

        """
        if self.input != other.input:
            raise ValueError("Input does not match")
        return self.__class__(self.input, [i for i in self._data if i not in other])

    def __eq__(self, other: object) -> bool:
        """Check if two configurations are equal.

        Args:
            other: The other configuration to compare with.

        Returns:
            True if the configurations are equal, False otherwise.

        """
        if not isinstance(other, Configuration):
            raise TypeError("Incompatible types")
        if self.input != other.input:
            raise ValueError("Input does not match")
        return self._data == other._data

    def __hash__(self) -> int:
        """Get the hash of the configuration.

        Returns:
            The hash of the configuration.

        """
        return hash(tuple(self._data))

    def __str__(self) -> str:
        """Get a string representation of the configuration.

        Returns:
            A string representation of the configuration.

        """
        return str(self._data)

    def __repr__(self) -> str:
        """Get a detailed string representation of the configuration.

        Returns:
            A detailed string representation of the configuration.

        """
        return repr(self._data)

    @property
    def data(self) -> Sequence[Any]:
        """Get the data of the configuration.

        Returns:
            The data of the configuration.

        """
        return self.input[self]
