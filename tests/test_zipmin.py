import doctest

from delta_debugging import Configuration, Debugger, Input, Outcome, ZipMin


def oracle(config: Configuration) -> Outcome:
    s: str = "".join(config.data)
    print(s, end=" ")
    for i in range(10):
        if str(i) not in s:
            print("Pass")
            return Outcome.PASS
    print("Fail")
    return Outcome.FAIL


def test_zipmin() -> None:
    input: Input = Input(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHI"
    )
    debugger: Debugger = Debugger(ZipMin(), oracle)
    debugger.debug(input)
    assert "".join(input[debugger.result]) == "1234567890"


def test_docstring() -> None:
    import delta_debugging.algorithms.zipmin

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.algorithms.zipmin, verbose=True
    )
    assert results.failed == 0
