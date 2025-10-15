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
    return outcome


def main() -> None:
    test_case: TestCase = TestCase(
        list(range(10)),
        [DDMin(), ZipMin()],
        [None],
        Debugger,
        oracle=oracle,
    )
    benchmark: Benchmark = Benchmark([test_case])
    benchmark.run()
    print(benchmark.to_string(floatfmt=".7f"))


if __name__ == "__main__":
    main()
