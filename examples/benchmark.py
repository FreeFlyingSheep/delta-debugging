import logging

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
    s: str = "".join(config)
    for i in range(10):
        if str(i) not in s:
            return Outcome.PASS
    return Outcome.FAIL


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    test_case: TestCase = TestCase(
        list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHI"),
        [DDMin(), ZipMin()],
        [None],
        Debugger,
        oracle=oracle,
    )
    benchmark: Benchmark = Benchmark([test_case])
    benchmark.run()
    print(benchmark.results.to_string(floatfmt=".7f"))


if __name__ == "__main__":
    main()
