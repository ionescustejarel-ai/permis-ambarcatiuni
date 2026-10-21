"""Tests marked `anr` read the official ANR question lists, which this repository
does not redistribute. Download them into sources/anr/ (see README) to run them."""
from pathlib import Path

import pytest

ANR = Path(__file__).resolve().parents[1] / "sources" / "anr"
HAVE_ANR = all((ANR / name).is_file() for name in ("lista_C.pdf", "lista_D.pdf"))


def pytest_configure(config):
    config.addinivalue_line("markers", "anr: needs the official ANR lists in sources/anr/")


def pytest_collection_modifyitems(config, items):
    if HAVE_ANR:
        return
    skip = pytest.mark.skip(reason="ANR lists not in sources/anr/ — see README, 'Data'")
    for item in items:
        if "anr" in item.keywords:
            item.add_marker(skip)
