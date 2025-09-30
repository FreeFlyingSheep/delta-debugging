"""ddmin delta debugging algorithm."""

import logging
from typing import Callable, Generator

from delta_debugging.algorithm import Algorithm
from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.input import Input
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

    def _complements(
        self, config: Configuration, granularity: int
    ) -> Generator[Configuration, None, None]:
        """Generate complementary configurations by dividing the configuration into `granularity` parts and removing each part in turn.

        Args:
            config: The original configuration.
            granularity: The level of granularity for the complements.

        Yields:
            A generator of complementary configurations.

        """
        start: int = 0
        for i in range(granularity):
            end: int = start + (len(config) - start) // (granularity - i)
            yield config[:start] + config[end:]
            start: int = end

    def run(
        self,
        input: Input,
        oracle: Callable[[Configuration], Outcome],
        *,
        cache: Cache | None = None,
    ) -> Configuration:
        """Run the ddmin algorithm.

        Args:
            input: Input to reduce.
            oracle: The oracle function.
            cache: Cache for storing test outcomes.

        Returns:
            The reduced configuration.

        """
        logger.debug("Starting ddmin algorithm")
        config: Configuration = Configuration.from_input(input)
        granularity: int = 2

        while len(config) >= 2:
            reducible: bool = False

            for complement in self._complements(config, granularity):
                outcome: Outcome = self._test(oracle, complement, cache=cache)
                logger.debug(
                    f"Testing complement with granularity {granularity}: {complement} => {outcome}"
                )
                if outcome == Outcome.FAIL:
                    config = complement
                    granularity = max(granularity - 1, 2)
                    reducible = True
                    break

            if reducible:
                continue

            if granularity < len(config):
                granularity = min(granularity * 2, len(config))
            else:
                break

        logger.debug(f"ddmin algorithm completed with reduced configuration: {config}")
        return config
