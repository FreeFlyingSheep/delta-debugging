import doctest


def test_docstring() -> None:
    import delta_debugging.parser

    results: doctest.TestResults = doctest.testmod(delta_debugging.parser, verbose=True)
    assert results.failed == 0
