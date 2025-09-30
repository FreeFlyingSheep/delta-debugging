import doctest
from typing import Any, Sequence

from delta_debugging import Configuration, Debugger, DDMin, Input, Outcome


def oracle(config: Configuration) -> Outcome:
    data: Sequence[Any] = config.data
    outcome: Outcome = Outcome.PASS
    if 5 not in data:
        outcome = Outcome.UNRESOLVED
    elif 3 in data and 7 in data:
        outcome = Outcome.FAIL
    print(data, outcome)
    return outcome


def test_ddmin() -> None:
    input: Input = Input(list(range(10)))
    debugger: Debugger = Debugger(DDMin(), oracle)
    debugger.debug(input)
    print(debugger.to_string())
    print(debugger.result)
    assert debugger.result == Configuration(input, [3, 5, 7])


def test_docstring() -> None:
    import delta_debugging.algorithms.ddmin

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.algorithms.ddmin, verbose=True
    )
    assert results.failed == 0
