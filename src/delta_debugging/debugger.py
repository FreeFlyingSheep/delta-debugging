"""Debugger class for delta debugging."""

import logging
from re import T
import time
from collections import Counter
from typing import Callable, TypeVar

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from delta_debugging.algorithm import Algorithm
from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.input import Input
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


class Debugger:
    """Debugger class."""

    algorithm: Algorithm
    """Algorithm to use for delta debugging."""
    oracle: Callable[[Configuration], Outcome]
    """Oracle function to determine the outcome of a configuration."""
    cache: Cache | None
    """Cache for storing test results."""
    counters: Counter[Outcome]
    """Counter for the number of tests per outcome."""
    time: float
    """Total time (in seconds) taken for debugging."""
    input: Input
    """Input to be reduced."""
    result: Configuration
    """Resulting reduced configuration."""
    _pbar: tqdm | None
    """Progress bar for showing the debugging process."""
    Type_Debugger = TypeVar("Type_Debugger", bound="Debugger")
    """@private Type variable for the debugger class."""

    def __init__(
        self,
        algorithm: Algorithm,
        oracle: Callable[[Configuration], Outcome],
        *,
        cache: Cache | None = None,
    ) -> None:
        """Initialize the debugger.

        Args:
            algorithm: Algorithm to use for delta debugging.
            oracle: Oracle function to determine the outcome of a configuration.
            cache: Cache for storing test outcomes.

        """
        self.algorithm = algorithm
        self.cache = cache
        self.oracle = oracle
        self.counters = Counter()
        self.time = 0.0
        self.input = Input([])
        self.result = Configuration.empty(self.input)
        self._pbar = None

    @classmethod
    def make(
        cls: type[Type_Debugger],
        algorithm: Algorithm,
        *,
        cache: Cache | None = None,
        **kwargs,
    ) -> Type_Debugger:
        """Create a debugger instance.

        Args:
            algorithm: Algorithm to use for delta debugging.
            cache: Cache for storing test outcomes.
            **kwargs: Additional arguments to pass to the debugger constructor.

        Returns:
            An instance of the debugger class.

        """
        return cls(algorithm, cache=cache, **kwargs)

    def _oracle(self, config: Configuration) -> Outcome:
        """Test the given configuration and update the counters and process bar.

        Args:
            config: Configuration to test.

        Returns:
            Outcome of the test.

        """
        outcome: Outcome = self.oracle(config)
        self.counters[outcome] += 1

        if self._pbar is not None:
            self._pbar.update(1)
            self._pbar.set_postfix(
                {str(outcome): count for outcome, count in self.counters.items()}
            )

        return outcome

    def debug(self, input: Input, *, show_process: bool = False) -> Configuration:
        """Run the debugger on the given input, showing the process if specified.

        Args:
            input: Input to be reduced.
            show_process: Whether to show the debugging process.

        Returns:
            The reduced configuration.

        """
        with logging_redirect_tqdm():
            if show_process:
                self._pbar = tqdm(
                    total=None,
                    unit="tests",
                    desc=f"Delta debugging using {self.algorithm}",
                    dynamic_ncols=True,
                )

            self.input = input
            start_time: float = time.time()
            self.result = self.algorithm.run(input, self._oracle, cache=self.cache)
            self.time = time.time() - start_time

            if self._pbar is not None:
                self._pbar.close()
                self._pbar = None

        return self.result

    def to_string(self) -> str:
        """Get a string representation of the debugger."""
        output: list[str] = [f"Delta debugging using {self.algorithm}"]
        output.append(
            f"Reduced input length from {len(self.input)} to {len(self.result)}"
        )
        output.append(
            f"Reduced ratio: {(len(self.input) - len(self.result)) / len(self.input):.2%}"
        )
        output.append(f"Total time: {self.time:.2f} seconds")
        return "\n".join(output)
