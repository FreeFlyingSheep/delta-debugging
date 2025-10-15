"""Kaitai Struct ELF parser."""

import logging
from io import BytesIO

from kaitaistruct import KaitaiStream

from delta_debugging.configuration import Configuration
from delta_debugging.parser import Node
from delta_debugging.parsers.kaitai_struct_compiled.elf import Elf


logger: logging.Logger = logging.getLogger(__name__)


def _parse_header(elf: Elf, root: Node) -> None:
    """Parse the ELF header and add it to the tree.

    Args:
        elf: Parsed ELF file.
        root: Root node of the tree.

    """
    logger.debug("Parsing ELF header")

    if not hasattr(elf.header, "e_ehsize"):
        return

    node: Node = Node("ELF Header", 0, elf.header.e_ehsize, root.depth + 1)
    root.children.append(node)


def _parse_pht(elf: Elf, root: Node) -> None:
    """Parse the Program Header Table (PHT) and add it to the tree.

    Args:
        elf: Parsed ELF file.
        root: Root node of the tree.

    """
    logger.debug("Parsing Program Header Table")

    if (
        not hasattr(elf.header, "ofs_program_headers")
        or not hasattr(elf.header, "program_header_size")
        or not hasattr(elf.header, "num_program_headers")
        or elf.header.num_program_headers == 0
    ):
        return

    pht_start: int = elf.header.ofs_program_headers
    size: int = elf.header.program_header_size
    pht_end: int = pht_start + elf.header.num_program_headers * size
    node: Node = Node("Program Header Table", pht_start, pht_end, root.depth + 1)
    root.children.append(node)

    if elf.header.program_headers is not None:
        for i in range(len(elf.header.program_headers)):
            start: int = pht_start + i * size
            end: int = start + size
            child: Node = Node(f"PHDR[{i}]", start, end, node.depth + 1)
            node.children.append(child)


def _parse_sections(elf: Elf, root: Node) -> bool:
    """Parse the sections and add them to the tree.

    Args:
        elf: Parsed ELF file.
        root: Root node of the tree.

    Returns:
        True if sections were found and added, False otherwise.

    """
    logger.debug("Parsing sections")

    if elf.header.section_headers is None:
        return False

    node: Node = Node("Sections", root.end, root.start, root.depth + 1)
    root.children.append(node)

    for i, sh in enumerate(elf.header.section_headers):
        if (
            not hasattr(sh, "ofs_body")
            or not hasattr(sh, "len_body")
            or sh.len_body == 0
        ):
            continue
        start: int = sh.ofs_body
        end: int = start + sh.len_body
        child: Node = Node(f"SEC[{i}]", start, end, root.depth + 1)
        node.children.append(child)

        node.start = min(node.start, start)
        node.end = max(node.end, end)

    if len(node.children) == 0:
        root.children.remove(node)
        return False

    return True


def _parse_segments(elf: Elf, root: Node) -> None:
    """Parse the segments and add them to the tree.

    Args:
        elf: Parsed ELF file.
        root: Root node of the tree.

    """
    logger.debug("Parsing segments")

    if elf.header.program_headers is None:
        return

    node: Node = Node("Segments", root.end, root.start, root.depth + 1)
    root.children.append(node)

    pht_end: int = 0
    for child in root.children:
        if child.name == "Program Header Table":
            pht_end = child.end
            break

    for i, ph in enumerate(elf.header.program_headers):
        if (
            not hasattr(ph, "offset")
            or not hasattr(ph, "filesz")
            or ph.filesz == 0
            or ph.offset < pht_end
        ):
            continue
        start: int = ph.offset
        end: int = start + ph.filesz
        child: Node = Node(f"SEG[{i}]", start, end, node.depth + 1)
        node.children.append(child)

        node.start = min(node.start, start)
        node.end = max(node.end, end)

    if len(node.children) == 0:
        root.children.remove(node)


def _parse_sht(elf: Elf, root: Node) -> None:
    """Parse the Section Header Table (SHT) and add it to the tree.

    Args:
        elf: Parsed ELF file.
        root: Root node of the tree.

    """
    logger.debug("Parsing Section Header Table")

    if (
        not hasattr(elf.header, "ofs_section_headers")
        or not hasattr(elf.header, "section_header_size")
        or not hasattr(elf.header, "num_section_headers")
        or elf.header.num_section_headers == 0
    ):
        return

    sht_start: int = int(elf.header.ofs_section_headers)
    size: int = int(elf.header.section_header_size)
    sht_end: int = sht_start + elf.header.num_section_headers * size
    node: Node = Node("Section Header Table", sht_start, sht_end, root.depth + 1)
    root.children.append(node)

    if elf.header.section_headers is not None:
        for i in range(len(elf.header.section_headers)):
            ent_start: int = sht_start + i * size
            ent_end: int = ent_start + size
            child: Node = Node(f"SHT[{i}]", ent_start, ent_end, node.depth + 1)
            node.children.append(child)


def parse_elf(config: Configuration) -> Node:
    """Parse an ELF file and return its tree representation.

    Args:
        config: Configuration representing the ELF file.

    Returns:
        Root node of the tree representation.

    """
    logger.debug("Parsing ELF file")

    elf: Elf = Elf(KaitaiStream(BytesIO(bytes(config))))

    root: Node = Node("ELF", 0, len(config), 0)

    _parse_header(elf, root)
    _parse_pht(elf, root)
    if not _parse_sections(elf, root):
        logger.warning("No sections found in ELF file, falling back to segments")
        _parse_segments(elf, root)
    _parse_sht(elf, root)

    return root
