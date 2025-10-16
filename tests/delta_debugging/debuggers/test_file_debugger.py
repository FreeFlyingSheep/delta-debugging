import doctest


def test_docstring() -> None:
    import delta_debugging.debuggers.file

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.debuggers.file, verbose=True
    )
    assert results.failed == 0
