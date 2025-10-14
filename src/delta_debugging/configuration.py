"""Configuration for delta debugging."""

import logging
from collections.abc import Sequence
from typing import Any, Iterator, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from delta_debugging.input import Input


logger: logging.Logger = logging.getLogger(__name__)


class Configuration(Sequence):
    """Configuration of an input.

    A configuration is a subset of the input, represented by a sequence of indices.
    The indices must be sorted and unique to ensure that the configuration is valid.
    To validate the indices, set `validate_indices` to True, which will decrease performance.
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
        >>> config2 = Configuration(input, [2])
        >>> print(config1 + config2)
        (0, 1, 2)
        >>> print(config1 - config2)
        (0, 1)
        >>> config3 = Configuration(input, [3])
        >>> print(config1.concat(config2, config3))
        (0, 1, 2, 3)

    """

    input: "Input"
    """The input associated with this configuration."""
    _data: tuple[int, ...]
    """The sorted and deduplicated indices of the input."""

    def __init__(
        self, input: "Input", indices: Sequence[int], *, validate_indices: bool = False
    ) -> None:
        """Initialize the configuration with the given indices.

        Args:
            input: The input to create the configuration for.
            indices: The indices of the input that are included in this configuration.
            validate_indices: If True, validate that the indices are sorted and unique.

        Raises:
            ValueError: If `validate_indices` is True and the indices are not sorted or contain duplicates.

        """
        if validate_indices:
            for i in range(len(indices) - 1):
                if indices[i] >= indices[i + 1]:
                    raise ValueError("Indices must be sorted and unique")

        self.input = input
        self._data = tuple(indices)

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

        merged: list[int] = list(self._data)
        merged.extend(other._data)
        return type(self)(self.input, merged)

    def concat(self, *other: "Configuration") -> "Configuration":
        """Concatenate multiple configurations.

        Args:
            other: Other configurations to concatenate.

        Returns:
            A new configuration that is the concatenation of the configurations.

        """
        merged: list[int] = list(self._data)
        for config in other:
            if config.input != self.input:
                raise ValueError("Input does not match")

            merged.extend(config._data)
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
        return hash(self._data)

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
