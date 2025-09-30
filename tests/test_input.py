import doctest


def test_docstring() -> None:
    import delta_debugging.input

    results: doctest.TestResults = doctest.testmod(delta_debugging.input, verbose=True)
    assert results.failed == 0
