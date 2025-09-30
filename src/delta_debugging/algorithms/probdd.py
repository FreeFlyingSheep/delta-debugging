"""Probabilistic Delta Debugging (ProbDD) algorithm."""

import logging
from math import log
from typing import Callable

from delta_debugging.algorithm import Algorithm
from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.input import Input
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


class ProbDD(Algorithm):
    """ProbDD algorithm.

    Examples:
        >>> from delta_debugging import ProbDD
        >>> str(ProbDD())
        'ProbDD'

    """

    def __str__(self) -> str:
        """Get the string representation of the ProbDD algorithm.

        Returns:
            Name of the algorithm.

        """
        return "ProbDD"

    def _sample(self, input: Input, probabilities: dict[int, float]) -> Configuration:
        """Sample a configuration based on the given probabilities.

        Args:
            input: Input to sample from.
            probabilities: Probabilities for each element in the input.

        Returns:
            Sampled configuration.

        """
        config: Configuration = Configuration.empty(input)
        keys: list[int] = list(probabilities.keys())

        last: float = 0.0
        i: int = 0
        k: int = 0
        while i < len(probabilities):
            if probabilities[keys[i]] == 0.0:
                i += 1
                k += 1
                continue

            if probabilities[keys[i]] >= 1.0:
                break

            prob: float = 1.0
            for j in range(k, i + 1):
                prob *= 1 - probabilities[keys[j]]
            prob *= i - k + 1
            if prob < last:
                break

            last = prob
            i += 1

        while i > k:
            i -= 1
            config += Configuration(input, [keys[i]])

        return config

    def _ratio(self, deleted, probabilities) -> float:
        """Calculate the ratio of the probabilities of the deleted elements.

        Args:
            deleted: Deleted configuration.
            probabilities: Probabilities for each element.

        Returns:
            Ratio of the probabilities.

        """
        ratio: float = 1.0
        for d in deleted:
            if probabilities[d] > 0 and probabilities[d] < 1:
                ratio *= 1 - probabilities[d]
        return 1 / (1 - ratio)

    def run(
        self,
        input: Input,
        oracle: Callable[[Configuration], Outcome],
        *,
        cache: Cache | None = None,
    ) -> Configuration:
        """Run the ProbDD algorithm.

        Args:
            input: Input to reduce.
            oracle: The oracle function.
            cache: Cache for storing test outcomes.

        Returns:
            The reduced configuration.

        """
        logger.debug("Starting ProbDD algorithm")
        config: Configuration = Configuration.from_input(input)
        passed: Configuration = Configuration.from_input(input)
        probabilities: dict[int, float] = {}
        threshold: float = 0.8
        for c in config:
            probabilities[c] = 0.1

        while True:
            probs: set[float] = set(probabilities.values())
            if probs == {0.0} or probs == {1.0} or probs == {0.0, 1.0}:
                break

            convergence: bool = True
            for probability in probabilities.values():
                if probability < threshold:
                    convergence = False
                    break

            if convergence:
                break

            probabilities = dict(
                sorted(probabilities.items(), key=lambda item: item[1])
            )
            logger.debug(f"Current probabilities: {probabilities}")

            deleted: Configuration = self._sample(input, probabilities)
            logger.debug(f"Sampling configuration: {deleted}")

            config = passed - deleted
            outcome: Outcome = self._test(oracle, config, cache=cache)
            logger.debug(f"Testing configuration: {config} => {outcome}")
            if outcome == Outcome.FAIL:
                for key in probabilities.keys():
                    if key not in config:
                        probabilities[key] = 0.0
                passed = config
                continue

            for key in probabilities.keys():
                if (
                    key not in config
                    and probabilities[key] != 0.0
                    and probabilities[key] != 1.0
                ):
                    probabilities[key] = (
                        probabilities[key]
                        + (self._ratio(deleted, probabilities) - 1) * probabilities[key]
                    )

            if len(deleted) == 1:
                for d in deleted:
                    probabilities[d] = 1.0

        logger.debug(f"ProbDD algorithm completed with reduced configuration: {passed}")
        return passed
