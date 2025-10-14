"""File based debugger for delta debugging."""

import logging
import os
from subprocess import CompletedProcess
from typing import Any, Callable, Sequence

from delta_debugging.algorithm import Algorithm
from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.debuggers import CommandDebugger
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


class FileDebugger(CommandDebugger):
    """File based debugger.

    This debugger writes the current configuration to a temporary file
    and appends the file name to the command before executing it. After execution,
    the temporary file is deleted.
    """

    file: str | os.PathLike
    """File to write the configuration to."""
    binary: bool
    """Whether to write the file in binary mode."""
    executable: bool
    """Whether to make the file executable."""

    def __init__(
        self,
        algorithm: Algorithm,
        command: list[str],
        file: str | os.PathLike,
        check: Callable[[CompletedProcess], Outcome],
        *,
        cache: Cache | None = None,
        timeout: float | None = None,
        binary: bool = False,
        executable: bool = False,
    ) -> None:
        """Initialize the file based debugger.

        Args:
            algorithm: Algorithm to use for delta debugging.
            command: Command to run as a list of strings.
            file: File to write the configuration to.
            check: Function to check the result of the command.
            cache: Cache for storing test outcomes.
            timeout: Timeout for the command in seconds. If None, no timeout is set.
            binary: Whether to write the file in binary mode.
            executable: Whether to make the file executable.

        """
        super().__init__(
            algorithm,
            command,
            check,
            cache=cache,
            timeout=timeout,
            pre_check=self._pre_check,
            post_check=self._post_check,
        )
        """Initialize the file based debugger.

        Args:
            algorithm: Algorithm to use for delta debugging.
            command: Command to run as a list of strings.
            check: Function to check the result of the command.
            cache: Cache for storing test outcomes.
            timeout: Timeout for the command in seconds. If None, no timeout is set.
            pre_check: Function to run before the command is executed.
            post_check: Function to run after the command is executed.

        """

        self.file = file
        self.binary = binary
        self.executable = executable

    def write(self, file: str | os.PathLike, config: Configuration) -> None:
        """Write the configuration to the given file.

        Args:
            file: File to write the configuration to.
            config: Configuration to write.

        """
        if self.binary:
            logger.debug(f"Writing configuration to binary file: {file}")
            with open(file, "wb") as f:
                f.write(bytes(config.data))
            logger.debug(f"Setting executable permission for file: {file}")
            if self.executable:
                os.chmod(file, 0o755)
        else:
            logger.debug(f"Writing configuration to file: {file}")
            with open(file, "w") as f:
                f.write(str(config.data))

    def _pre_check(self, config: Configuration, command: list[str]) -> None:
        """Prepare the command for execution by writing the configuration to a temporary file.

        Args:
            config: Configuration to use for the command.
            command: Command to modify.

        """
        self.write(self.file, config)
        command.append(str(self.file))

    def _post_check(self, config: Configuration, command: list[str]) -> None:
        """Clean up after the command execution by deleting the temporary file.

        Args:
            config: Configuration to use for the command.
            command: Command to modify.

        """
        if os.path.exists(self.file):
            os.remove(self.file)
        command.pop()
