import json
from subprocess import CompletedProcess
from typing import Any, Callable

from delta_debugging import (
    Algorithm,
    Benchmark,
    DDMin,
    HDD,
    KaitaiStructParser,
    ProbDD,
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


def add_test_cases(test_cases: list[TestCase], bug: dict[str, Any]) -> None:
    if bug["skip"]:
        return

    algorithms: list[Algorithm] = [
        DDMin(),
        ZipMin(),
        ProbDD(),
        HDD(KaitaiStructParser("ELF"), DDMin()),
        HDD(KaitaiStructParser("ELF"), ZipMin()),
        HDD(KaitaiStructParser("ELF"), ProbDD()),
    ]
    args: dict[str, Any] = {
        "file": bug["file"],
        "directory": "/tmp",
        "algorithms": algorithms,
        "command": bug["command"],
        "check": check(bug),
        "caches": [None],
        "timeout": bug["timeout"],
        "binary": True,
        "executable": True,
        "replace": None,
    }
    test_cases.append(TestCase.make_file(**args))
    args["replace"] = b"0x00"
    test_cases.append(TestCase.make_file(**args))


def main() -> None:
    test_cases: list[TestCase] = []

    with open("examples/valgrind_bugs/bugs.json", "r") as f:
        data: Any = json.load(f)
        for bug in data:
            add_test_cases(test_cases, bug)

    benchmark: Benchmark = Benchmark(test_cases, "/tmp/results.json")
    benchmark.run(show_process=True)
    print(benchmark.to_string())


if __name__ == "__main__":
    main()
