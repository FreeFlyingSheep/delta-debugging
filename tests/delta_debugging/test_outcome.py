import doctest


def test_docstring() -> None:
    import delta_debugging.outcome

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.outcome, verbose=True
    )
    assert results.failed == 0
