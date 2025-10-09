"""Benchmark for delta debugging algorithms."""

import itertools
import json
import logging
import os
from dataclasses import dataclass
from subprocess import CompletedProcess
from typing import Any, Callable, Generator, Self

from tabulate import tabulate

from delta_debugging.algorithm import Algorithm
from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration
from delta_debugging.debugger import Debugger
from delta_debugging.debuggers import CommandDebugger, FileDebugger
from delta_debugging.input import Input
from delta_debugging.outcome import Outcome


logger: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Result:
    """Result of a test case run."""

    algorithm: str
    """Name of the algorithm used."""
    cache: str
    """Name of the cache used."""
    input_size: int
    """Size of the input."""
    output_size: int
    """Size of the output."""
    count: int
    """Number of calls to the oracle function."""
    time: float
    """Time (in seconds) taken for the test case run."""

    @property
    def reduction_ratio(self) -> float:
        """Compute the reduction ratio.

        If the input size is 0, the reduction ratio is defined to be 1.0.

        Returns:
            The reduction ratio.

        """
        if self.input_size == 0:
            return 1.0
        else:
            return (self.input_size - self.output_size) / self.input_size

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        """Create a Result instance from a JSON dictionary.

        Args:
            data: JSON dictionary.

        Returns:
            A Result instance.

        """
        return cls(
            algorithm=data["algorithm"],
            cache=data["cache"],
            input_size=data["input_size"],
            output_size=data["output_size"],
            count=data["count"],
            time=data["time"],
        )

    def to_json(self) -> dict[str, float | int | str]:
        """Convert the result to a JSON-serializable dictionary.

        Returns:
            A JSON-serializable dictionary representation of the result.

        """
        result: dict[str, float | int | str] = {
            "algorithm": self.algorithm,
            "cache": self.cache,
            "input_size": self.input_size,
            "output_size": self.output_size,
            "reduction_ratio": self.reduction_ratio,
            "count": self.count,
            "time": self.time,
        }
        return result


class TestCase:
    """A test case for a benchmark."""

    __test__: bool = False
    """Prevent pytest from collecting this class as a test case."""

    input: Input
    """Input to be reduced."""
    debuggers: list[Debugger]
    """List of debuggers to benchmark."""

    def __init__(
        self,
        input: Input,
        algorithms: list[Algorithm],
        caches: list[Cache | None],
        debugger_cls: type[Debugger],
        **kwargs,
    ) -> None:
        """Initialize the test case. Create a list of debuggers to benchmark.

        Args:
            input: Input to be reduced.
            algorithms: List of algorithms to benchmark.
            caches: List of caches to use.
            debugger_cls: Debugger class to use.
            **kwargs: Additional arguments to pass to the debugger.

        """
        self.input = input
        self.debuggers = []
        for algorithm, cache in itertools.product(algorithms, caches):
            self.debuggers.append(debugger_cls.make(algorithm, cache=cache, **kwargs))

    @classmethod
    def make_command(
        cls,
        input: Input,
        algorithms: list[Algorithm],
        caches: list[Cache | None],
        command: list[str],
        check: Callable[[CompletedProcess], Outcome],
        timeout: float | None = None,
    ) -> Self:
        """Create a test case for a command-line based debugger.

        Args:
            input: Input to be reduced.
            algorithms: List of algorithms to benchmark.
            caches: List of caches to use.
            command: Command to run the program to be debugged.
            check: Function to check the outcome of the command.
            timeout: Timeout for the command.

        Returns:
            A test case instance with a command-line based debugger.

        """
        return cls(
            input=input,
            algorithms=algorithms,
            caches=caches,
            debugger_cls=CommandDebugger,
            command=command,
            check=check,
            timeout=timeout,
        )

    @classmethod
    def make_file(
        cls,
        algorithms: list[Algorithm],
        caches: list[Cache | None],
        file: str | os.PathLike,
        directory: str | os.PathLike,
        command: list[str],
        check: Callable[[CompletedProcess], Outcome],
        timeout: float | None = None,
        binary: bool = False,
        executable: bool = False,
        replace: bytes | str | None = None,
    ) -> Self:
        """Create a test case for a file-based debugger.

        Args:
            algorithms: List of algorithms to benchmark.
            caches: List of caches to use.
            file: File to be reduced.
            directory: Directory to save temporary files to.
            command: Command to run the program to be debugged.
            check: Function to check the outcome of the command.
            timeout: Timeout for the command.
            binary: Whether to read the file in binary mode.
            executable: Whether to make the temporary file executable.
            replace: Value to replace in the configuration. If None, no replacement is done.

        Returns:
            A test case instance with a file-based debugger.

        """
        input: Input = Input.from_file(file, executable=executable)
        return cls(
            input=input,
            algorithms=algorithms,
            caches=caches,
            debugger_cls=FileDebugger,
            file=file,
            directory=directory,
            command=command,
            check=check,
            timeout=timeout,
            binary=binary,
            executable=executable,
            replace=replace,
        )

    def validate(self) -> bool:
        """Validate the input for all debuggers.

        Returns:
            True if the input triggers the bug, False otherwise.

        """
        triggered: bool = True
        for debugger in self.debuggers:
            if not debugger.validate(self.input):
                triggered = False
                break
        return triggered

    def iter_run(self, *, show_process: bool = False) -> Generator[Result, None, None]:
        """Run the test case and yield results for each debugger.

        Args:
            show_process: Whether to show the debugging process.

        Yields:
            Result of each benchmark run.

        """
        test_id: int = 0
        for debugger in self.debuggers:
            logger.debug(f"Running debugger with algorithm: {debugger.algorithm}")
            config: Configuration = debugger.debug(
                self.input, show_process=show_process
            )
            test_id += 1

            yield Result(
                algorithm=str(debugger.algorithm),
                cache=str(debugger.cache) if debugger.cache is not None else "None",
                input_size=len(self.input),
                output_size=len(config),
                count=sum(debugger.counters.values()),
                time=debugger.time,
            )


class Benchmark:
    """A benchmark for delta debugging algorithms."""

    test_cases: list[TestCase]
    """List of test cases to benchmark."""
    file: str | os.PathLike | None
    """File to save results to."""
    results: list[Result]
    """List of results from benchmark runs."""

    def __init__(
        self, test_cases: list[TestCase], file: str | os.PathLike | None = None
    ) -> None:
        """Initialize the benchmark.

        Args:
            test_cases: List of test cases to benchmark.
            file: File to save results to.

        """
        self.test_cases = test_cases
        self.file = file
        self.results = []

    def validate(self) -> list[bool]:
        """Validate the input for each test case.

        Returns:
            List of validation results. True if the input triggers the bug, False otherwise.

        """
        results: list[bool] = []
        for test_case in self.test_cases:
            results.append(test_case.validate())
        return results

    def run(self, *, show_process: bool = False) -> list[Result]:
        """Run the benchmark and save results to file if specified.

        Args:
            show_process: Whether to show the debugging process.

        Returns:
            List of results from benchmark runs.

        """
        logger.debug("Starting benchmark")
        results: list[dict[str, float | int | str]] = []
        for test_case in self.test_cases:
            for result in test_case.iter_run(show_process=show_process):
                self.results.append(result)
                results.append(result.to_json())
                if self.file is not None:
                    with open(self.file, "w") as f:
                        try:
                            json.dump(results, f, indent=4)
                        except Exception:
                            logger.exception("Error writing benchmark results to file")
                            return self.results
        logger.debug("Benchmark completed")
        return self.results

    def read_results(self, file: str | os.PathLike | None) -> list[Result]:
        """Read results from file or the benchmark's file if specified.

        Args:
            file: File to read results from. If None, use the benchmark's file. If both are None, results will be empty.

        """
        results: list[dict[str, float | int | str]] = []
        try:
            if file is not None:
                logger.debug(f"Reading results from file: {file}")
                with open(file, "r") as f:
                    results = json.load(f)
            elif self.file is not None:
                logger.debug(f"Reading results from file: {self.file}")
                with open(self.file, "r") as f:
                    results = json.load(f)
            else:
                logger.debug(
                    "No file specified for reading results; results will be empty"
                )
                results = []
        except Exception:
            logger.exception("Error reading benchmark results from file")
            self.results = []
            return self.results

        self.results = [Result.from_json(result) for result in results]
        return self.results

    def to_string(self, **kwargs) -> str:
        """Get a string representation of the benchmark results.

        Args:
            kwargs: Additional arguments to pass to tabulate. Defaults are:
                headers: "keys"
                floatfmt: ".2f"
                showindex: "always"

        """
        results: list[dict[str, float | int | str]] = [
            result.to_json() for result in self.results
        ]
        if "headers" not in kwargs:
            kwargs["headers"] = "keys"
        if "floatfmt" not in kwargs:
            kwargs["floatfmt"] = ".2f"
        if "showindex" not in kwargs:
            kwargs["showindex"] = "always"
        return tabulate(results, **kwargs)
