from typing import Any, Sequence

from delta_debugging import (
    Benchmark,
    Configuration,
    DDMin,
    Debugger,
    Input,
    Outcome,
    TestCase,
    ZipMin,
)


def oracle(config: Configuration) -> Outcome:
    data: Sequence[Any] = config.data
    outcome: Outcome = Outcome.PASS
    if 5 not in data:
        outcome = Outcome.UNRESOLVED
    elif 3 in data and 7 in data:
        outcome = Outcome.FAIL
    print(data, outcome)
    return outcome


def test_benchmark() -> None:
    input: Input = Input(list(range(10)))
    test_case: TestCase = TestCase(
        input,
        [DDMin(), ZipMin()],
        [None],
        Debugger,
        oracle=oracle,
    )
    benchmark: Benchmark = Benchmark([test_case])
    assert all(benchmark.validate())
