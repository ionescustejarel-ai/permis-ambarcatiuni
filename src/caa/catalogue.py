"""What the three catalogues do the same way.

`signals.py`, `figures.py` and `arcs.py` each hold entries that quote the bank
verbatim, and each has to answer the same two questions: which entry does a
given question belong to, and does every quote still exist. Written three
times, those answers drifted — the same design defect had to be found and
fixed twice, in two catalogues, by two different reviewers. A fourth
catalogue is coming.

What is deliberately *not* here: the coverage rules. Their shapes genuinely
differ — sound patterns live only in the answer, marks and arcs in either
field, and the arc rule carries a negative guard the others have no use for.
Forcing them together would put the subtlety somewhere nobody looks, which is
the failure this module exists to prevent, not to cause.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from caa.normalize import normalize_key


def index_by_source(entries: Iterable[tuple[str, Sequence[str]]]) -> dict[str, str]:
    """Normalized quote -> entry id, for every quote every entry carries.

    Two entries claiming the same quote would silently shadow one another, so
    each catalogue's tests assert that they do not. This does not check it:
    the check belongs where the data is, not where the lookup is.
    """
    index: dict[str, str] = {}
    for entry_id, sources in entries:
        for source in sources:
            index[normalize_key(source)] = entry_id
    return index


def resolve(index: dict[str, str], entries: Iterable[Sequence[str]]) -> dict[str, str]:
    """Maps question id -> entry id, over however many fields a catalogue uses.

    Each entry is `(question id, *texts)`. A catalogue whose quotes are always
    answers passes one text; one whose quotes appear in the question as often
    as in the answer passes both. Every text is tried whole — a field that
    merely contains a quoted phrase is a different field, and matching on
    fragments would put a neighbouring question under the wrong entry.

    Two fields naming *different* entries raises. No such question exists in
    any catalogue today, and the alternative was worse than an exception:
    taking whichever field was tried first is not a policy, and the losing
    entry would be dropped without a word. If an edition of the bank ever
    creates one, somebody has to decide what the question is about.
    """
    found: dict[str, str] = {}
    for entry in entries:
        question_id, texts = entry[0], entry[1:]
        matched = {index[key] for key in map(normalize_key, texts) if key in index}
        if len(matched) > 1:
            raise ValueError(f"{question_id}: fields name {sorted(matched)}")
        if matched:
            found[question_id] = matched.pop()
    return found


def orphan_sources(
    entries: Iterable[tuple[str, Sequence[str]]], texts: Iterable[str]
) -> list[tuple[str, str]]:
    """Quotes that no longer appear in the bank, as (entry id, quote) pairs.

    The catalogues quote the bank verbatim. If ANR reworded an answer, the
    quote stops matching and the entry would attach to nothing at all — so
    every catalogue's audit rule stops the build on what this returns.
    """
    present = {normalize_key(text) for text in texts}
    return [
        (entry_id, source)
        for entry_id, sources in entries
        for source in sources
        if normalize_key(source) not in present
    ]


def announcing(texts: Sequence[str], announces) -> list[str]:
    """The fields that actually announce whatever the caller is looking for.

    A coverage finding must quote one of these and not simply the last field
    it happened to hold: naming the innocent neighbour sends whoever reads the
    report to excuse the wrong text. That went wrong once for marks and was
    caught in review; stating it once here is cheaper than catching it again.
    """
    return [text for text in texts if announces(text)]
