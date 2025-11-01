import doctest


def test_docstring() -> None:
    import delta_debugging.result

    results: doctest.TestResults = doctest.testmod(delta_debugging.result, verbose=True)
    assert results.failed == 0
