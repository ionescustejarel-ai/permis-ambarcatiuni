import pytest
"""Verifies the package layout and test runner are wired correctly."""

from pathlib import Path


@pytest.mark.anr
def test_source_pdfs_are_present():
    root = Path(__file__).resolve().parents[2]
    assert (root / "sources" / "anr" / "lista_C.pdf").is_file()
    assert (root / "sources" / "anr" / "lista_D.pdf").is_file()


def test_caa_package_imports():
    import caa

    assert caa is not None


def test_no_source_file_carries_a_bom_or_mojibake():
    """An implementer's editor once round-tripped audit.py through Windows-1252.

    The result shipped: a BOM, the report's own Romanian heading double-encoded
    in the text the audit actually prints, and a dozen mangled docstrings — invisible
    to a suite that only asserts ASCII substrings. This is the guard: every
    tracked source file is BOM-free UTF-8 with no double-encoding residue.
    """
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    # Every Romanian letter this project writes, in the form cp1252 leaves it.
    # The first version listed four and missed \u0219, \u0218, \u0102 and \u021a \u2014 the letters most
    # likely to appear in a statement of theory, which is the one text in the
    # application checked byte-for-byte against nothing.
    residue = ("\u00c3", "\u00e2\u20ac",
               "\u00c8\u2122", "\u00c8\u203a", "\u00c8\u02dc", "\u00c8\u0161",
               "\u00c4\u0192", "\u00c4\u201a")
    scanned = 0
    for folder, suffixes in (("src/caa", (".py", ".js", ".css", ".html")), ("tests", (".py", ".js"))):
        for path in (root / folder).rglob("*"):
            if path.suffix not in suffixes:
                continue
            raw = path.read_bytes()
            assert not raw.startswith(b"\xef\xbb\xbf"), f"{path.name}: BOM"
            text = raw.decode("utf-8")
            for marker in residue:
                assert marker not in text, f"{path.name}: mojibake {marker!r}"
            scanned += 1
    # A renamed directory makes rglob yield nothing, and a walk over zero files
    # passes every assertion it never reaches.
    assert scanned > 40, f"scanned only {scanned} files"
