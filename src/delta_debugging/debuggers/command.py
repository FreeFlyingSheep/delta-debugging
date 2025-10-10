"""Command line based debugger for delta debugging."""

import logging
import subprocess
from subprocess import CompletedProcess, TimeoutExpired
from typing import Callable

from delta_debugging.algorithm import Algorithm
from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.debugger import Debugger
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


class CommandDebugger(Debugger):
    """Command line based debugger.

    This debugger runs a command line program with the given configuration
    and checks the outcome using the provided check function.
    Use the `pre_check` and `post_check` functions to modify the command
    before and after execution, respectively.
    Timeouts can be handled using the `timeout_handler` function.
    """

    command: list[str]
    """Command to run as a list of strings."""
    check: Callable[[CompletedProcess], Outcome]
    """Function to check the result of the command."""
    timeout: float | None
    """Timeout for the command in seconds."""
    pre_check: Callable[[Configuration, list[str]], None] | None
    """Function to run before the command is executed."""
    post_check: Callable[[Configuration, list[str]], None] | None
    """Function to run after the command is executed."""
    timeout_handler: Callable[[Configuration, list[str]], Outcome] | None
    """Function to handle timeouts."""
    _command: list[str]
    """Original command to run."""

    def __init__(
        self,
        algorithm: Algorithm,
        command: list[str],
        check: Callable[[CompletedProcess], Outcome],
        *,
        cache: Cache | None = None,
        timeout: float | None = None,
        pre_check: Callable[[Configuration, list[str]], None] | None = None,
        post_check: Callable[[Configuration, list[str]], None] | None = None,
        timeout_handler: Callable[[Configuration, list[str]], Outcome] | None = None,
    ) -> None:
        """Initialize the command line based debugger.

        Args:
            algorithm: Algorithm to use for delta debugging.
            command: Command to run as a list of strings.
            check: Function to check the result of the command.
            cache: Cache for storing test outcomes.
            timeout: Timeout for the command in seconds. If None, no timeout is set.
            pre_check: Function to run before the command is executed.
            post_check: Function to run after the command is executed.
            timeout_handler: Function to handle timeouts. If None, timeouts are treated as UNRESOLVED.

        """
        super().__init__(algorithm, self._check, cache=cache)
        self.command: list[str] = command
        self.check: Callable[[CompletedProcess], Outcome] = check
        self.timeout: float | None = timeout
        self.pre_check: Callable[[Configuration, list[str]], None] | None = pre_check
        self.post_check: Callable[[Configuration, list[str]], None] | None = post_check
        self.timeout_handler: Callable[[Configuration, list[str]], Outcome] | None = (
            timeout_handler
        )
        self._command: list[str] = command[:]

    def _check(self, config: Configuration) -> Outcome:
        """Check the outcome of the command with the given configuration.

        Args:
            config: Configuration to test.

        Returns:
            Outcome of the command.

        """
        if self.pre_check is not None:
            logger.debug(
                f"Running pre_check for configuration {config} command {self.command}"
            )
            self.pre_check(config, self.command)
            logger.debug(f"Command after pre_check: {self.command}")

        try:
            result: CompletedProcess[bytes] = subprocess.run(
                " ".join(self.command),
                capture_output=True,
                shell=True,
                timeout=self.timeout,
            )
        except TimeoutExpired:
            if self.timeout_handler is not None:
                logger.debug(
                    f"Running timeout_handler for configuration {config} with command {self.command}"
                )
                outcome: Outcome = self.timeout_handler(config, self.command)
                logger.debug(f"Outcome from timeout_handler: {outcome}")
                return outcome
            return Outcome.UNRESOLVED

        outcome: Outcome = self.check(result)
        if self.post_check is not None:
            logger.debug(
                f"Running post_check for configuration {config} with command {self.command}"
            )
            self.post_check(config, self.command)
            logger.debug(f"Outcome from post_check: {outcome}")

        self.command = self._command[:]
        return outcome
