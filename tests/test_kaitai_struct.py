import doctest

from delta_debugging import KaitaiStructParser


def test_kaitai_struct_parser() -> None:
    try:
        KaitaiStructParser(" Not Supported ")
    except ValueError as e:
        print(e)
        assert "Unsupported binary format: not supported." in str(e)


def test_docstring() -> None:
    import delta_debugging.parsers.kaitai_struct

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.parsers.kaitai_struct, verbose=True
    )
    assert results.failed == 0
