"""Normalization helpers used for comparison only.

The PDFs mix diacritic encodings: some sections use ș/ț (comma below,
U+0219/U+021B), others ş/ţ (cedilla, U+015F/U+0163), and some drop
diacritics entirely. Normalized keys make those forms compare equal.

Displayed text is never normalized — only keys are.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata

# A run of separators collapses to a single space. Replacing them one by
# one would leave double spaces and break equality between duplicates.
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_key(text: str) -> str:
    """Returns a comparison key: no diacritics, no punctuation, lowercase."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return _NON_ALNUM.sub(" ", stripped.lower()).strip()


def question_id(question: str) -> str:
    """Returns a stable id derived from the question text.

    Stability matters: saved progress in localStorage is keyed by this id
    and must survive a rebuild that adds or removes other questions.
    """
    digest = hashlib.sha256(normalize_key(question).encode("utf-8")).hexdigest()
    return f"q{digest[:12]}"
