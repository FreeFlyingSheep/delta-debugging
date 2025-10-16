import doctest

from delta_debugging import Configuration, Debugger, Outcome, ProbDD


def oracle(config: Configuration) -> Outcome:
    outcome: Outcome = Outcome.PASS
    if 3 not in config or 5 not in config or 7 not in config:
        outcome = Outcome.UNRESOLVED
    elif 13 in config and 15 in config and 17 in config:
        outcome = Outcome.FAIL
    print(config, outcome)
    return outcome


def test_probdd() -> None:
    debugger: Debugger = Debugger(ProbDD(), oracle)
    debugger.debug(list(range(20)))
    print(debugger.to_string())
    print(debugger.result)
    assert debugger.result == [3, 5, 7, 13, 15, 17]


def test_docstring() -> None:
    import delta_debugging.algorithms.probdd

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.algorithms.probdd, verbose=True
    )
    assert results.failed == 0
