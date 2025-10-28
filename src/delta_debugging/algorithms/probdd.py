"""Probabilistic Delta Debugging (ProbDD) algorithm."""

import logging
from collections.abc import MutableMapping
from typing import Any, Callable

from delta_debugging.algorithm import Algorithm
from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


class Probability(MutableMapping):
    """Probability mapping for configuration elements."""

    def __init__(self, *, to_tuple: bool) -> None:
        """Initialize the Probability mapping.

        Args:
            to_tuple: Whether to convert keys to tuples.

        """
        self._data: dict[Any, float] = {}
        self._to_tuple: bool = to_tuple

    def __getitem__(self, key: Any) -> float:
        """Get the probability for a given key.

        Args:
            key: Key to get the probability for.

        Returns:
            Probability value.

        """
        if self._to_tuple:
            key = tuple(key)
        return self._data[key]

    def __setitem__(self, key: Any, value: float) -> None:
        """Set the probability for a given key.

        Args:
            key: Key to set the probability for.
            value: Probability value to set.

        """
        if self._to_tuple:
            key = tuple(key)
        self._data[key] = value

    def __delitem__(self, key: Any) -> None:
        """Delete the probability for a given key.

        Args:
            key: Key to delete the probability for.

        """
        if self._to_tuple:
            key = tuple(key)
        del self._data[key]

    def __iter__(self):
        """Iterate over the keys in the mapping.

        Returns:
            Iterator over the keys.

        """
        return iter(self._data)

    def __len__(self) -> int:
        """Get the number of items in the mapping.

        Returns:
            Number of items.

        """
        return len(self._data)

    def key_list(self) -> list[Any]:
        """Get the list of keys.

        Returns:
            List of keys.

        """
        if self._to_tuple:
            return [list(key) for key in self._data.keys()]
        else:
            return list(self._data.keys())

    def sort(self) -> None:
        """Sort the mapping by values."""
        self._data = dict(sorted(self._data.items(), key=lambda item: item[1]))


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

    def _sample(self, probabilities: Probability) -> Configuration:
        """Sample a configuration based on the given probabilities.

        Args:
            probabilities: Probabilities for each element in the configuration.

        Returns:
            Sampled configuration.

        """
        c: Configuration = []
        keys: list[Any] = probabilities.key_list()
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
                prob *= 1.0 - probabilities[keys[j]]
            prob *= i - k + 1
            if prob < last:
                break

            last = prob
            i += 1

        while i > k:
            i -= 1
            c.append(keys[i])

        return c

    def _ratio(self, deleted: Configuration, probabilities: Probability) -> float:
        """Calculate the ratio of the probabilities of the deleted elements.

        Args:
            deleted: Deleted configuration.
            probabilities: Probabilities for each element.

        Returns:
            Ratio of the probabilities.

        """
        ratio: float = 1.0
        for d in deleted:
            if probabilities[d] > 0.0 and probabilities[d] < 1.0:
                ratio *= 1.0 - probabilities[d]
        return 1.0 / (1.0 - ratio)

    def _difference(
        self, config1: Configuration, config2: Configuration, *, to_tuple: bool = False
    ) -> Configuration:
        """Get the difference between two configurations.

        Args:
            config1: First configuration.
            config2: Second configuration.
            to_tuple: Whether to convert elements to tuples.

        Returns:
            Difference between the two configurations.

        """
        if to_tuple:
            config: set[Any] = set()
            for c in config2:
                config.add(tuple(c))
            return [c for c in config1 if tuple(c) not in config]
        else:
            config = set(config2)
            return [c for c in config1 if c not in config]

    def _stop(self, probabilities: Probability, threshold: float) -> bool:
        """Check if the algorithm should stop based on the probabilities and threshold.

        Args:
            probabilities: Probabilities for each element.
            threshold: Threshold for stopping.

        Returns:
            Whether the algorithm should stop.

        """
        probs: set[float] = set(probabilities.values())
        if probs in ({0.0}, {1.0}, {0.0, 1.0}):
            return True

        convergence: bool = True
        for probability in probabilities.values():
            if probability < threshold:
                convergence = False
                break

        if convergence:
            return True

        return False

    def run(
        self,
        config: Configuration,
        oracle: Callable[[Configuration], Outcome],
        *,
        cache: Cache | None = None,
    ) -> Configuration:
        """Run the ProbDD algorithm.

        Args:
            config: Configuration to reduce.
            oracle: The oracle function.
            cache: Cache for storing test outcomes.

        Returns:
            The reduced configuration.

        """
        logger.debug("Starting ProbDD algorithm")
        passed: Configuration = list(config)
        to_tuple: bool = len(config) > 0 and isinstance(config[0], list)
        probabilities: Probability = Probability(to_tuple=to_tuple)
        threshold: float = 0.8
        for c in config:
            probabilities[c] = 0.1

        while True:
            if self._stop(probabilities, threshold):
                break

            probabilities.sort()
            logger.debug(f"Current probabilities: {probabilities}")

            deleted: Configuration = self._sample(probabilities)
            logger.debug(f"Sampling configuration: {deleted}")

            config = self._difference(passed, deleted, to_tuple=to_tuple)
            outcome: Outcome = self._test(oracle, config, cache=cache)
            logger.debug(f"Testing configuration: {config} => {outcome}")
            if outcome == Outcome.FAIL:
                for key in probabilities.key_list():
                    if key not in config:
                        probabilities[key] = 0.0
                passed = config
                continue

            for key in probabilities.key_list():
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
