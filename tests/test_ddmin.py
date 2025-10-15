import doctest

from delta_debugging import Configuration, Debugger, DDMin, Outcome


def oracle(config: Configuration) -> Outcome:
    outcome: Outcome = Outcome.PASS
    if 5 not in config:
        outcome = Outcome.UNRESOLVED
    elif 3 in config and 7 in config:
        outcome = Outcome.FAIL
    print(config, outcome)
    return outcome


def test_ddmin() -> None:
    debugger: Debugger = Debugger(DDMin(), oracle)
    debugger.debug(list(range(10)))
    print(debugger.to_string())
    print(debugger.result)
    assert debugger.result == [3, 5, 7]


def test_docstring() -> None:
    import delta_debugging.algorithms.ddmin

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.algorithms.ddmin, verbose=True
    )
    assert results.failed == 0
