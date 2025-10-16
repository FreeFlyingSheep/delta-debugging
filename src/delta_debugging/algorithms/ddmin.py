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
        num: int,
        oracle: Callable[[Configuration], Outcome],
        *,
        cache: Cache | None = None,
    ) -> Configuration:
        """Remove and check each fragment of the configuration.

        Args:
            config: The current configuration.
            num: Number of fragments.
            oracle: The oracle function.
            cache: Cache for storing test outcomes.

        Returns:
            The updated configuration after removing fragments that do not affect the failure.

        """
        pre: Configuration = []
        for i in range(0, len(config), num):
            removed, remaining = config[i : i + num], config[i + num :]
            outcome: Outcome = self._test(oracle, pre + remaining, cache=cache)
            logger.debug(
                f"Testing configuration by removing fragments: {config} => {outcome}"
            )
            if outcome != Outcome.FAIL:
                pre += removed
        return pre

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
        num: int = len(config) // 2
        while num and config:
            reduced: Configuration = self._remove_check_each_fragment(
                config, num, oracle, cache=cache
            )
            if reduced == config:
                num = num // 2
            config = reduced

        logger.debug(f"ddmin algorithm completed with reduced configuration: {config}")
        return config
