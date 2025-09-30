import json
from typing import Any

from delta_debugging import Benchmark, DDMin, Outcome, TestCase, ZipMin


def main() -> None:
    test_cases: list[TestCase] = []

    with open("examples/bugs.json", "r") as f:
        data: Any = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Invalid bugs.json format")

        for bug in data:
            if not isinstance(bug, dict):
                raise ValueError("Invalid bugs.json format")
            if "file" not in bug or not isinstance(bug["file"], str):
                raise ValueError("Invalid bugs.json format")
            if "command" not in bug or not isinstance(bug["command"], list):
                for cmd in bug["command"]:
                    if not isinstance(cmd, str):
                        raise ValueError("Invalid bugs.json format")
            if "error" not in bug or not isinstance(bug["error"], str):
                raise ValueError("Invalid bugs.json format")
            if "timeout" not in bug or not isinstance(bug["timeout"], float):
                raise ValueError("Invalid bugs.json format")
            if "url" not in bug or not isinstance(bug["url"], str):
                raise ValueError("Invalid bugs.json format")
            if "skip" not in bug and isinstance(bug["skip"], bool):
                raise ValueError("Invalid bugs.json format")

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

    benchmark: Benchmark = Benchmark(test_cases, "/tmp/bugs_results.json")
    benchmark.run(show_process=True)
    print(benchmark.to_string())


if __name__ == "__main__":
    main()
