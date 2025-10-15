"""Configuration for delta debugging."""

import logging
import os
from typing import Any

logger: logging.Logger = logging.getLogger(__name__)


type Configuration = list[Any]
"""A configuration is a list of elements."""


def load(file: str | os.PathLike, *, binary: bool = False) -> Configuration:
    """Load a configuration from a file.

    Args:
        file: File to load the configuration from.
        binary: Whether to read the file in binary mode.

    Returns:
        Configuration loaded from the file.

    """
    if binary:
        logger.debug(f"Loading configuration from binary file: {file}")
        with open(file, "rb") as f:
            bytes_data: bytes = f.read()
            return list(bytes_data)
    else:
        logger.debug(f"Loading configuration from file: {file}")
        with open(file, "r") as f:
            str_data: str = f.read()
            return list(str_data)
