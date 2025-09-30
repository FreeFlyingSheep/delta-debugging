"""Abstract algorithm class for delta debugging."""

import logging
from abc import ABC, abstractmethod
from typing import Callable

from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.input import Input
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


class Algorithm(ABC):
    """Abstract algorithm class."""

    @abstractmethod
    def __str__(self) -> str:
        """Get the string representation of the algorithm.

        Returns:
            Name of the algorithm.

        """
        pass

    @abstractmethod
    def run(
        self,
        input: Input,
        oracle: Callable[[Configuration], Outcome],
        *,
        cache: Cache | None = None,
    ) -> Configuration:
        """Run the algorithm on the given input.

        Args:
            input: Input to reduce.
            oracle: The oracle function.
            cache: Cache for storing test outcomes.

        Returns:
            The reduced configuration.

        """
        pass

    def _test(
        self,
        oracle: Callable[[Configuration], Outcome],
        config: Configuration,
        *,
        cache: Cache | None = None,
    ) -> Outcome:
        """Test the given configuration using the oracle function and cache the result if needed.

        Args:
            oracle: The oracle function.
            config: Configuration to test.
            cache: Cache for storing test outcomes.

        Returns:
            The outcome of the test.

        Raises:
            Exception: If the oracle function raises an exception.

        """
        try:
            if cache is not None and config in cache:
                outcome: Outcome = cache[config]
            else:
                outcome = oracle(config)
                if cache is not None:
                    cache[config] = outcome
            return outcome
        except Exception as e:
            logger.error("Error during oracle evaluation")
            raise e
