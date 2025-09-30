import doctest


def test_docstring() -> None:
    import delta_debugging.algorithm

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.algorithm, verbose=True
    )
    assert results.failed == 0
