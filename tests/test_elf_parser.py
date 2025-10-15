import doctest
from delta_debugging import KaitaiStructParser, Node


def test_elf() -> None:
    elf: bytes = (
        b"\x7f\x45\x4c\x46\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x02\x00\x3e\x00\x01\x00\x00\x00\x78\x00\x40\x00\x00\x00\x00\x00"
        b"\x40\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x40\x00\x38\x00\x01\x00\x40\x00\x00\x00\x00\x00"
        b"\x01\x00\x00\x00\x05\x00\x00\x00\x78\x00\x00\x00\x00\x00\x00\x00"
        b"\x78\x00\x40\x00\x00\x00\x00\x00\x78\x00\x40\x00\x00\x00\x00\x00"
        b"\x20\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\xb0\x01\x40\x88\xc7\xbe\x8a\x00"
        b"\x40\x00\xb2\x0e\x0f\x05\xb0\x01\xcd\x80\x48\x65\x6c\x6c\x6f\x2c"
        b"\x20\x57\x6f\x72\x6c\x64\x21\x0a"
    )
    parser: KaitaiStructParser = KaitaiStructParser("ELF")
    root: Node = parser.parse(list(elf))
    print(root.to_string())
    assert root.name == "ELF"
    assert root.start == 0
    assert root.end == len(elf)
    assert len(root.children) == 3
    assert root.children[0].name == "ELF Header"
    assert root.children[0].start == 0
    assert root.children[0].end == 64
    assert len(root.children[0].children) == 64
    assert root.children[1].name == "Program Header Table"
    assert root.children[1].start == 64
    assert root.children[1].end == 120
    assert len(root.children[1].children) == 1
    assert root.children[2].name == "Segments"
    assert root.children[2].start == 120
    assert root.children[2].end == 152
    assert len(root.children[2].children) == 1
    assert len(root.children[2].children[0].children) == 32


def test_docstring() -> None:
    import delta_debugging.parsers.kaitai_structs.elf

    results: doctest.TestResults = doctest.testmod(
        delta_debugging.parsers.kaitai_structs.elf, verbose=True
    )
    assert results.failed == 0
