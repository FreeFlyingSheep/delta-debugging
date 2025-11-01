"""Benchmark for delta debugging algorithms."""

import itertools
import logging
import os
from collections import Counter

from subprocess import CompletedProcess
from typing import Callable, Generator, Self

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from delta_debugging.algorithm import Algorithm
from delta_debugging.cache import Cache
from delta_debugging.configuration import Configuration, load
from delta_debugging.debugger import Debugger
from delta_debugging.debuggers import CommandDebugger, FileDebugger
from delta_debugging.outcome import Outcome
from delta_debugging.result import Result, ResultCollection


logger: logging.Logger = logging.getLogger(__name__)


class TestCase:
    """A test case for a benchmark."""

    __test__: bool = False
    """Prevent pytest from collecting this class as a test case."""

    config: Configuration
    """Configuration to be reduced."""
    debuggers: list[Debugger]
    """List of debuggers to benchmark."""

    def __init__(
        self,
        config: Configuration,
        algorithms: list[Algorithm],
        caches: list[Cache | None],
        debugger_cls: type[Debugger],
        **kwargs,
    ) -> None:
        """Initialize the test case. Create a list of debuggers to benchmark.

        Args:
            config: Configuration to be reduced.
            algorithms: List of algorithms to benchmark.
            caches: List of caches to use.
            debugger_cls: Debugger class to use.
            **kwargs: Additional arguments to pass to the debugger.

        """
        self.config = config
        self.debuggers = []
        for algorithm, cache in itertools.product(algorithms, caches):
            self.debuggers.append(debugger_cls.make(algorithm, cache=cache, **kwargs))

    @classmethod
    def make_command(
        cls,
        config: Configuration,
        algorithms: list[Algorithm],
        caches: list[Cache | None],
        command: list[str],
        check: Callable[[CompletedProcess], Outcome],
        timeout: float | None = None,
    ) -> Self:
        """Create a test case for a command-line based debugger.

        Args:
            config: Configuration to be reduced.
            algorithms: List of algorithms to benchmark.
            caches: List of caches to use.
            command: Command to run the program to be debugged.
            check: Function to check the outcome of the command.
            timeout: Timeout for the command.

        Returns:
            A test case instance with a command-line based debugger.

        """
        return cls(
            config=config,
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
        input_file: str | os.PathLike,
        output_file: str | os.PathLike,
        command: list[str],
        check: Callable[[CompletedProcess], Outcome],
        timeout: float | None = None,
        binary: bool = False,
        executable: bool = False,
    ) -> Self:
        """Create a test case for a file-based debugger.

        Args:
            algorithms: List of algorithms to benchmark.
            caches: List of caches to use.
            input_file: File to be reduced.
            output_file: File to write the reduced input to.
            command: Command to run the program to be debugged.
            check: Function to check the outcome of the command.
            timeout: Timeout for the command.
            binary: Whether to read the file in binary mode.
            executable: Whether to make the temporary file executable.

        Returns:
            A test case instance with a file-based debugger.

        """
        config: Configuration = load(input_file, binary=binary)
        return cls(
            config=config,
            algorithms=algorithms,
            caches=caches,
            debugger_cls=FileDebugger,
            file=output_file,
            command=command,
            check=check,
            timeout=timeout,
            binary=binary,
            executable=executable,
        )

    def iter_validate(self) -> Generator[bool, None, None]:
        """Validate the input for all debuggers.

        Yields:
            True if the input triggers the bug, False otherwise.

        """
        for debugger in self.debuggers:
            yield debugger.validate(self.config)

    def iter_run(self, *, show_process: bool = False) -> Generator[Result, None, None]:
        """Run the test case and yield results for each debugger.

        Args:
            show_process: Whether to show the debugging process.

        Yields:
            Result of each benchmark run.

        """
        for debugger in self.debuggers:
            logger.debug(f"Running debugger with algorithm: {debugger.algorithm}")
            config: Configuration = debugger.debug(
                self.config, show_process=show_process
            )

            file: str = "None"
            if isinstance(debugger, FileDebugger):
                file: str = str(debugger.file)
            cache: str = "None"
            if debugger.cache is not None:
                cache = str(debugger.cache)

            yield Result(
                file=file,
                algorithm=str(debugger.algorithm),
                cache=cache,
                input_size=len(self.config),
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
    results: ResultCollection
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
        self.results = ResultCollection()

    def validate(self, show_process: bool = False) -> list[bool]:
        """Validate the input for each test case.

        Args:
            show_process: Whether to show the validation process.

        Returns:
            List of validation results. True if the input triggers the bug, False otherwise.

        """
        pbar: tqdm | None = None
        total: int = sum(len(test_case.debuggers) for test_case in self.test_cases)
        with logging_redirect_tqdm(loggers=[logger]):
            if show_process:
                pbar = tqdm(
                    total=total,
                    desc="Validating",
                    unit="test cases",
                )

        results: list[bool] = []
        counter: Counter[bool] = Counter()
        for test_case in self.test_cases:
            for result in test_case.iter_validate():
                results.append(result)
                counter[result] += 1
                if pbar is not None:
                    pbar.update(1)
                    pbar.set_postfix(
                        {
                            str(triggered): str(count)
                            for triggered, count in counter.items()
                        }
                    )

        if pbar is not None:
            pbar.close()

        return results

    def run(self, *, show_process: bool = False) -> ResultCollection:
        """Run the benchmark and save results to file if specified.

        Args:
            show_process: Whether to show the debugging process.

        Returns:
            List of results from benchmark runs.

        """
        logger.debug("Starting benchmark")
        total: int = sum(len(test_case.debuggers) for test_case in self.test_cases)
        pbar: tqdm | None = None
        with logging_redirect_tqdm(loggers=[logger]):
            if show_process:
                pbar: tqdm | None = tqdm(
                    total=total, desc="Benchmarking", unit="test cases"
                )
        for test_case in self.test_cases:
            for result in test_case.iter_run(show_process=show_process):
                self.results.add(result)

                logger.info(f"Current Results {len(self.results)}/{total}:")
                messages: list[str] = self.results.to_string().splitlines()
                for message in messages:
                    logger.info(message)

                if self.file is not None:
                    self.results.store_results(self.file)

                if pbar is not None:
                    pbar.update(1)

        if pbar is not None:
            pbar.close()

        logger.debug("Benchmark completed")
        return self.results
