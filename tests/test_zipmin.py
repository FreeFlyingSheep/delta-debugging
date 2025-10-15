import doctest

from delta_debugging import Configuration, Debugger, Outcome, ZipMin


def oracle(config: Configuration) -> Outcome:
    s: str = "".join(config)
    print(s, end=" ")
    for i in range(10):
        if str(i) not in s:
            print("Pass")
            return Outcome.PASS
    print("Fail")
    return Outcome.FAIL


def test_zipmin() -> None:
    debugger: Debugger = Debugger(ZipMin(), oracle)
    debugger.debug(
        list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHI")
    )
    assert "".join(debugger.result) == "1234567890"


def test_docstring() -> None:
    import delta_debugging.algorithms.zipmin

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.algorithms.zipmin, verbose=True
    )
    assert results.failed == 0
