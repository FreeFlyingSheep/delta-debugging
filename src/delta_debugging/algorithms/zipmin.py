"""Zipmin delta debugging algorithm."""

import logging
from typing import Callable

from delta_debugging.algorithm import Algorithm
from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.input import Input
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


class ZipMin(Algorithm):
    """Zipmin algorithm.

    Examples:
        >>> str(ZipMin())
        'Zipmin'

    """

    def __str__(self) -> str:
        """Get the string representation of the Zipmin algorithm.

        Returns:
            Name of the algorithm.

        """
        return "Zipmin"

    def _remove_last_char(
        self,
        oracle: Callable[[Configuration], Outcome],
        pre: Configuration,
        config: Configuration,
        post: Configuration,
        *,
        cache: Cache | None = None,
    ) -> tuple[Configuration, Configuration, Configuration]:
        """Remove the last character from the configuration if it does not affect the failure.

        Args:
            oracle: The oracle function.
            pre: The prefix configuration.
            config: The current configuration.
            post: The postfix configuration.
            cache: Cache for storing test outcomes.

        Returns:
            A tuple of the updated prefix, configuration, and postfix.

        """
        c: Configuration = pre + config[:-1] + post
        outcome: Outcome = self._test(oracle, c, cache=cache)
        logger.debug(f"Testing configuration by removing last char: {c} => {outcome}")
        if outcome == Outcome.FAIL:
            return pre, config[:-1], post
        else:
            return pre, config[:-1], config[-1] + post

    def _remove_check_each_fragment(
        self,
        oracle: Callable[[Configuration], Outcome],
        pre: Configuration,
        config: Configuration,
        post: Configuration,
        length: int,
        *,
        cache: Cache | None = None,
    ) -> tuple[Configuration, int]:
        """Remove fragments of the configuration of the given length if they do not affect the failure.

        Args:
            oracle: The oracle function.
            pre: The prefix configuration.
            config: The current configuration.
            post: The postfix configuration.
            length: The length of fragments to remove.
            cache: Cache for storing test outcomes.

        Returns:
            A tuple of the updated configuration and the number of fragments removed.

        """
        c: Configuration = Configuration.empty(config.input)
        count: int = 0

        for i in range(0, len(config), length):
            removed, remaining = config[i : i + length], config[i + length :]
            conf: Configuration = pre + c + remaining + post
            outcome: Outcome = self._test(oracle, conf, cache=cache)
            logger.debug(
                f"Testing configuration by removing fragments: {conf} => {outcome}"
            )
            if outcome != Outcome.FAIL:
                c += removed
            else:
                count += 1

        return c, max(count - (len(config) - len(c)), 0)

    def run(
        self,
        input: Input,
        oracle: Callable[[Configuration], Outcome],
        *,
        cache: Cache | None = None,
    ) -> Configuration:
        """Run the Zipmin algorithm.

        Args:
            input: Input to reduce.
            oracle: The oracle function.
            cache: Cache for storing test outcomes.

        Returns:
            The reduced configuration.

        """
        logger.debug("Starting Zipmin algorithm")
        config: Configuration = Configuration.from_input(input)
        length: int = len(config) // 2
        count: int = 0
        deficit: int = 0
        pre: Configuration = Configuration.empty(config.input)
        post: Configuration = Configuration.empty(config.input)

        while length > 0 and len(config) > 0:
            c: Configuration = Configuration.empty(config.input)
            if count % 2:
                for _ in range(deficit):
                    pre, c, post = self._remove_last_char(
                        oracle, pre, config, post, cache=cache
                    )
                deficit = 0
            else:
                c, deficit = self._remove_check_each_fragment(
                    oracle, pre, config, post, length, cache=cache
                )
                if c == config:
                    length = length // 2
            config = c

        config = pre + config + post
        logger.debug(f"Zipmin algorithm completed with reduced configuration: {config}")
        return config
