from delta_debugging import (
    Benchmark,
    Configuration,
    DDMin,
    Debugger,
    Outcome,
    TestCase,
    ZipMin,
)


def oracle(config: Configuration) -> Outcome:
    outcome: Outcome = Outcome.PASS
    if 5 not in config:
        outcome = Outcome.UNRESOLVED
    elif 3 in config and 7 in config:
        outcome = Outcome.FAIL
    print(config, outcome)
    return outcome


def test_benchmark() -> None:
    test_case: TestCase = TestCase(
        list(range(10)),
        [DDMin(), ZipMin()],
        [None],
        Debugger,
        oracle=oracle,
    )
    benchmark: Benchmark = Benchmark([test_case])
    assert all(benchmark.validate())
