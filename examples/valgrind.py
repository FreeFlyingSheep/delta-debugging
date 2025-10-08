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


def check(error: dict[str, int | str]) -> Callable[[CompletedProcess], Outcome]:
    def _check(result: CompletedProcess) -> Outcome:
        match_returncode: bool = False
        match_stdout: bool = False
        match_stderr: bool = False
        if "returncode" not in error or result.returncode == error["returncode"]:
            match_returncode = True
        if "stdout" not in error or error["stdout"] in result.stdout.decode(
            errors="ignore"
        ):
            match_stdout = True
        if "stderr" not in error or error["stderr"] in result.stderr.decode(
            errors="ignore"
        ):
            match_stderr = True
        if match_returncode and match_stdout and match_stderr:
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
    test_cases.append(
        TestCase.make_file(
            file=bug["file"],
            directory="/tmp",
            algorithms=algorithms,
            command=bug["command"],
            check=check(bug["error"]),
            caches=[None],
            timeout=bug["timeout"],
            binary=True,
            executable=True,
            replace=None,
        )
    )
    test_cases.append(
        TestCase.make_file(
            file=bug["file"],
            directory="/tmp",
            algorithms=algorithms,
            command=bug["command"],
            check=check(bug["error"]),
            caches=[None],
            timeout=bug["timeout"],
            binary=True,
            executable=True,
            replace=b"0x00",
        )
    )


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
