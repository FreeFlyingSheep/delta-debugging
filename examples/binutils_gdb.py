import json
from typing import Any

from delta_debugging import Benchmark, DDMin, Outcome, TestCase, ZipMin


def main() -> None:
    test_cases: list[TestCase] = []

    with open("examples/binutils_gdb_bugs/bugs.json", "r") as f:
        data: Any = json.load(f)
        for bug in data:
            if bug["skip"]:
                continue

            test_cases.append(
                TestCase.make_file(
                    file=bug["file"],
                    directory="/tmp",
                    algorithms=[DDMin(), ZipMin()],
                    command=bug["command"],
                    check=lambda result: (
                        Outcome.FAIL
                        if bytes(bug["error"], "utf-8") in result.stderr
                        else Outcome.PASS
                    ),
                    caches=[None],
                    timeout=bug["timeout"],
                    binary=True,
                    executable=True,
                )
            )

    benchmark: Benchmark = Benchmark(test_cases, "/tmp/results.json")
    benchmark.run(show_process=True)
    print(benchmark.to_string())


if __name__ == "__main__":
    main()
