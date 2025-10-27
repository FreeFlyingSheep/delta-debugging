"""ddmin delta debugging algorithm."""

import logging
from typing import Callable

from delta_debugging.algorithm import Algorithm
from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


class DDMin(Algorithm):
    """ddmin algorithm.

    Examples:
        >>> from delta_debugging import DDMin
        >>> str(DDMin())
        'ddmin'

    """

    def __str__(self) -> str:
        """Get the string representation of the DDMin algorithm.

        Returns:
            Name of the algorithm.

        """
        return "ddmin"

    def _remove_check_each_fragment(
        self,
        config: Configuration,
        length: int,
        oracle: Callable[[Configuration], Outcome],
        *,
        cache: Cache | None = None,
    ) -> Configuration:
        """Remove and check each fragment of the configuration.

        Args:
            config: The current configuration.
            length: The length of fragments to remove.
            oracle: The oracle function.
            cache: Cache for storing test outcomes.

        Returns:
            The updated configuration after removing fragments that do not affect the failure.

        """
        c: Configuration = []
        for i in range(0, len(config), length):
            removed, remaining = config[i : i + length], config[i + length :]
            conf: Configuration = c + remaining
            outcome: Outcome = self._test(oracle, conf, cache=cache)
            logger.debug(
                f"Testing configuration by removing fragments: {conf} => {outcome}"
            )
            if outcome != Outcome.FAIL:
                c += removed
        return c

    def run(
        self,
        config: Configuration,
        oracle: Callable[[Configuration], Outcome],
        *,
        cache: Cache | None = None,
    ) -> Configuration:
        """Run the ddmin algorithm.

        Args:
            config: Configuration to reduce.
            oracle: The oracle function.
            cache: Cache for storing test outcomes.

        Returns:
            The reduced configuration.

        """
        logger.debug("Starting ddmin algorithm")
        length: int = len(config) // 2

        while length > 0 and len(config) > 0:
            c: Configuration = self._remove_check_each_fragment(
                config, length, oracle, cache=cache
            )
            if c == config:
                length = length // 2
            config = c

        logger.debug(f"ddmin algorithm completed with reduced configuration: {config}")
        return config
