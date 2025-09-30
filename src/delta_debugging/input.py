"""Input class for delta debugging."""

import logging
import os
from typing import Any, Self, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from delta_debugging.configuration import Configuration


logger: logging.Logger = logging.getLogger(__name__)


class Input:
    """A failure-inducing input.

    Examples:
        >>> from delta_debugging import Configuration, Input
        >>> input = Input([1, 2, 3])
        >>> config = Configuration(input, [0, 2])
        >>> print(input[config])
        [1, 3]
        >>> print(len(input))
        3

    """

    data: Sequence[Any]
    """Data of the input."""
    data_type: "type"
    """Type of the input data."""

    def __init__(self, data: Sequence[Any]) -> None:
        """Initialize the input.

        Args:
            data: Data of the input.

        """
        self.data = data
        self.data_type = type(data)

    @classmethod
    def from_file(cls, file: str | os.PathLike, *, executable: bool = False) -> Self:
        """Create an input from a file.

        Args:
            file: Path to the file.
            executable: Whether the file is executable (binary). Defaults to False.

        Returns:
            An input instance with the file data.

        """
        if executable:
            with open(file, "rb") as f:
                bytes_data: bytes = f.read()
            return cls(bytes_data)
        else:
            with open(file, "r") as f:
                str_data: str = f.read()
            return cls(str_data)

    def __getitem__(self, index: "Configuration") -> Sequence[Any]:
        """Get the data for the given configuration.

        Args:
            index: Configuration to get the data for.

        Returns:
            Data for the given configuration.

        Raises:
            KeyError: If the configuration does not match the input.

        """
        if index.input != self:
            raise KeyError("Configuration not matched")
        return [self.data[c] for c in index]

    def __len__(self) -> int:
        """Get the length of the input.

        Returns:
            Length of the input.

        """
        return len(self.data)
