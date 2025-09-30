import doctest
from typing import Any, Sequence

from delta_debugging import Configuration, Debugger, Input, Outcome, ProbDD


def oracle(config: Configuration) -> Outcome:
    data: Sequence[Any] = config.data
    outcome: Outcome = Outcome.PASS
    if 3 not in data or 5 not in data or 7 not in data:
        outcome = Outcome.UNRESOLVED
    elif 13 in data and 15 in data and 17 in data:
        outcome = Outcome.FAIL
    print(data, outcome)
    return outcome


def test_probdd() -> None:
    input: Input = Input(list(range(20)))
    debugger: Debugger = Debugger(ProbDD(), oracle)
    debugger.debug(input)
    print(debugger.to_string())
    print(debugger.result)
    assert debugger.result == Configuration(input, [3, 5, 7, 13, 15, 17])


def test_docstring() -> None:
    import delta_debugging.algorithms.probdd

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.algorithms.probdd, verbose=True
    )
    assert results.failed == 0
