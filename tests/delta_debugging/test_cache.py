import doctest


def test_docstring() -> None:
    import delta_debugging.cache

    results: doctest.TestResults = doctest.testmod(delta_debugging.cache, verbose=True)
    assert results.failed == 0
