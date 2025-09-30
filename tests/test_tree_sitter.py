import doctest

from delta_debugging import TreeSitterParser


def test_tree_sitter_parser() -> None:
    try:
        TreeSitterParser(" Not Supported ")
    except ValueError as e:
        print(e)
        assert "Unsupported language: not supported." in str(e)


def test_docstring() -> None:
    import delta_debugging.parsers.tree_sitter

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.parsers.tree_sitter, verbose=True
    )
    assert results.failed == 0
