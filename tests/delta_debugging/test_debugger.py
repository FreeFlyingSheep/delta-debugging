import doctest


def test_docstring() -> None:
    import delta_debugging.debugger

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.debugger, verbose=True
    )
    assert results.failed == 0
