import json
import logging
import os
from subprocess import CompletedProcess
from typing import Any, Callable

from delta_debugging import Benchmark, DDMin, Outcome, ProbDD, TestCase, ZipMin


def check(error: str) -> Callable[[CompletedProcess], Outcome]:
    def _check(result: CompletedProcess) -> Outcome:
        if error in result.stderr.decode("utf-8", errors="ignore"):
            return Outcome.FAIL
        return Outcome.PASS

    return _check


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    test_cases: list[TestCase] = []

    with open("examples/binutils_gdb_bugs/bugs.json", "r") as f:
        data: Any = json.load(f)
        for bug in data:
            if bug["skip"]:
                continue

            test_cases.append(
                TestCase.make_file(
                    input_file=bug["file"],
                    output_file=os.path.join("/tmp", os.path.basename(bug["file"])),
                    algorithms=[DDMin(), ZipMin(), ProbDD()],
                    command=bug["command"],
                    check=check(bug["error"]),
                    caches=[None],
                    timeout=bug["timeout"],
                    binary=True,
                    executable=True,
                )
            )

    benchmark: Benchmark = Benchmark(test_cases, "/tmp/results.json")
    validates: list[bool] = benchmark.validate()
    if not all(validates):
        print(validates)
        print("Some test cases are invalid. Please check the environment.")
        return

    benchmark.run(show_process=True)
    print(benchmark.to_string())


if __name__ == "__main__":
    main()
