"""Configuration for delta debugging."""

import heapq
import logging
from collections.abc import Sequence
from dataclasses import dataclass, field, InitVar
from typing import Any, Iterator, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from delta_debugging.input import Input


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Configuration(Sequence):
    """Configuration of an input.

    A configuration is an immutable subset of the input, represented by a sequence of indices.
    The indices must be sorted and unique to ensure that the configuration is valid.
    If multiple configurations are concatenated, use the `concat` method for efficiency.

    Examples:
        >>> from delta_debugging import Configuration, Input
        >>> input = Input([1, 2, 3, 4])
        >>> config1 = Configuration(input, [0, 1])
        >>> print(config1)
        (0, 1)
        >>> print(config1[0])
        (0,)
        >>> print(len(config1))
        2
        >>> print(config1.data)
        [1, 2]
        >>> config2 = Configuration(input, [1, 2])
        >>> print(config1 + config2)
        (0, 1, 2)
        >>> print(config1 - config2)
        (0,)
        >>> config3 = Configuration(input, [3])
        >>> print(config1.concat(config2, config3))
        (0, 1, 2, 3)

    """

    input: "Input"
    """The input associated with this configuration."""
    indices: InitVar[Sequence[int]] = ()
    """The indices of the input that are included in this configuration."""
    _data: tuple[int, ...] = field(init=False, repr=False, compare=True)
    """The sorted and deduplicated indices of the input."""
    _len: int = field(init=False, repr=False, compare=False)
    """The length of the configuration."""
    _hash: int = field(init=False, repr=False, compare=False)
    """The hash of the configuration."""

    def __post_init__(self, indices: Sequence[int]) -> None:
        """Initialize the configuration with the given indices.

        Args:
            indices: The indices of the input that are included in this configuration.

        Raises:
            ValueError: If the indices are not sorted or contain duplicates.

        """
        for i in range(len(indices) - 1):
            if indices[i] >= indices[i + 1]:
                raise ValueError("Indices must be sorted and unique")

        data: tuple[int, ...] = tuple(indices)
        object.__setattr__(self, "_data", data)
        object.__setattr__(self, "_len", len(data))
        object.__setattr__(self, "_hash", hash(data))

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
            return type(self)(self.input, self._data[index])
        else:
            return type(self)(self.input, [self._data[index]])

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
        return self._len

    def __add__(self, other: "Configuration") -> "Configuration":
        """Combine two configurations.

        Args:
            other: The other configuration to combine with.

        Returns:
            A new configuration that combines the two configurations.

        """
        if self.input != other.input:
            raise ValueError("Input does not match")

        merged: list[int] = []
        last: int = -1
        for x in heapq.merge(self._data, other._data):
            if x != last:
                merged.append(x)
                last = x
        return type(self)(self.input, merged)

    def concat(self, *other: "Configuration") -> "Configuration":
        """Concatenate multiple configurations.

        Args:
            other: Other configurations to concatenate.

        Returns:
            A new configuration that is the concatenation of the configurations.

        """
        if not all(other_input.input == self.input for other_input in other):
            raise ValueError("Input does not match")

        merged: list[int] = []
        last: int = -1
        for config in (self, *other):
            if config.input != self.input:
                raise ValueError("Input does not match")
            for x in config._data:
                if x != last:
                    merged.append(x)
                    last = x
        return type(self)(self.input, merged)

    def __sub__(self, other: "Configuration") -> "Configuration":
        """Get the difference between two configurations.

        Args:
            other: The other configuration to subtract.

        Returns:
            A new configuration that is the difference between the two configurations.

        """
        if self.input != other.input:
            raise ValueError("Input does not match")

        return type(self)(self.input, [d for d in self._data if d not in other._data])

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
        return self._hash

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
