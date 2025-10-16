import json
import logging
import os
from subprocess import CompletedProcess
from typing import Any, Callable

from delta_debugging import (
    Benchmark,
    DDMin,
    HDD,
    KaitaiStructParser,
    Outcome,
    TestCase,
    ZipMin,
)


def check(bug: dict[str, Any]) -> Callable[[CompletedProcess], Outcome]:
    def _check(result: CompletedProcess) -> Outcome:
        if "stderr" in bug and bug["stderr"] in result.stderr.decode(
            "utf-8", errors="ignore"
        ):
            return Outcome.FAIL
        elif "stdout" in bug and bug["stdout"] in result.stdout.decode(
            "utf-8", errors="ignore"
        ):
            return Outcome.FAIL
        return Outcome.PASS

    return _check


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    test_cases: list[TestCase] = []

    with open("examples/valgrind_bugs/bugs.json", "r") as f:
        data: Any = json.load(f)

        for bug in data:
            if bug["skip"]:
                continue

            test_cases.append(
                TestCase.make_file(
                    input_file=bug["file"],
                    output_file=os.path.join("/tmp", os.path.basename(bug["file"])),
                    algorithms=[
                        DDMin(),
                        ZipMin(),
                        HDD(KaitaiStructParser("ELF"), DDMin()),
                        HDD(KaitaiStructParser("ELF"), ZipMin()),
                    ],
                    command=bug["command"],
                    check=check(bug),
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
