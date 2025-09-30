"""Kaitai Struct parsers."""

from delta_debugging.parsers.kaitai_structs.elf import parse_elf


__all__: list[str] = [
    "parse_elf",
]
