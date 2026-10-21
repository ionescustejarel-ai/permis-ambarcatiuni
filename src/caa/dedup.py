"""Collapses duplicate questions, merging their classes and disciplines.

Two rows are the same question only when both the stem AND the set of
options match. The bank contains distinct questions that share a stem —
class C numbers 55, 56 and 57 all ask which vessels a sailing vessel must
keep clear of, each with its own three options and its own answer.
Grouping on the stem alone loses 47 questions across the bank.

Duplicates may list the options in a different order, so the option set is
sorted before it becomes part of the key, and equality of answers is
decided on the normalized text of the correct option — never on its index.

Where the two official lists disagree on the answer to an otherwise
identical question, the group is split into one item per class rather than
resolved: each class is examined from its own list, so the answer that
passes the exam is the one in the candidate's list. Those items carry
`disputed=True`. A list that contradicts itself, or a row with no single
marked option, is a real conflict: reported and dropped, so the audit can
fail the build.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from caa.normalize import normalize_key, question_id
from caa.structure import LocatedRow


# Rows kept out of the bank, with the reason. Excluding a row is a data-policy
# decision and belongs here, in the open — never a silent edit of the source text.
#
# lista_D nr 84 (page 5) renders "bordul tribord" as BOTH the first and the
# second option, with the second marked correct. A candidate who picks the first
# is failed for text identical to the right answer, so the question cannot be
# answered correctly by reading it. The same question with a sane option set is
# already in the bank — lista_D nr 103 and lista_C nr 226 both read "bordul
# babord" first, and the old bank in sources/arhiva/ agrees — and that item
# reaches both classes, so nothing is lost by dropping this one.
# Decision by the project owner, 2026-07-26.
EXCLUDED_ROWS: Final[frozenset[tuple[str, int, int]]] = frozenset({("D", 84, 5)})


@dataclass(frozen=True)
class Question:
    """A deduplicated question ready for theme assignment."""

    id: str
    question: str
    options: tuple[str, str, str]
    correct: int
    section: str
    disciplines: tuple[tuple[str, str], ...]
    classes: tuple[str, ...]
    disputed: bool = False
    theme: str | None = None

    def disciplines_for(self, exam_class: str) -> tuple[str, ...]:
        """The disciplines this question belongs to within one exam class."""
        return tuple(
            discipline for cls, discipline in self.disciplines if cls == exam_class
        )


@dataclass(frozen=True)
class DedupConflict:
    """Rows of one question that cannot be reconciled into a single answer."""

    key: str
    question: str
    correct_texts: tuple[str, ...]


def _correct_index(row: LocatedRow) -> int | None:
    """Returns the index of the single correct option, or None if malformed.

    A blank flag cell counts as "not correct": one row in lista_C renders an
    empty middle flag while still marking exactly one option.
    """
    marked = [i for i, flag in enumerate(row.flags) if flag == "1"]
    return marked[0] if len(marked) == 1 else None


def _group_key(row: LocatedRow) -> tuple[str, tuple[str, ...]]:
    """Same question only if the stem and the option set both match."""
    return (
        normalize_key(row.question),
        tuple(sorted(normalize_key(option) for option in row.options)),
    )


def _build(
    key: tuple[str, tuple[str, ...]],
    rows: list[LocatedRow],
    classes: tuple[str, ...],
    disputed: bool,
) -> Question:
    """Makes one Question from rows already known to agree on the answer.

    The id derives from the GROUP KEY, not from the representative row. The key
    is already canonical — normalized stem plus sorted normalized options — so
    every row of a group yields the same id. Building it from the
    representative's raw text instead made the id depend on which row happened
    to come first, because sorting raw options can differ from sorting
    normalized ones once diacritics are involved: 19 of 275 multi-row groups
    changed id depending on the representative. Saved progress is keyed by this
    id and must survive a rebuild, so it cannot depend on document order.
    """
    representative = rows[0]
    index = _correct_index(representative)
    assert index is not None  # callers only pass reconciled rows

    identity = " | ".join([key[0], *key[1]])
    if disputed:
        identity = f"{identity} | class {classes[0]}"

    return Question(
        id=question_id(identity),
        question=representative.question,
        options=representative.options,
        correct=index,
        section=representative.section,
        disciplines=tuple(sorted({(row.source, row.discipline) for row in rows})),
        classes=classes,
        disputed=disputed,
    )


def build_questions(
    rows: list[LocatedRow],
) -> tuple[list[Question], list[DedupConflict]]:
    """Groups rows by stem and option set, then reconciles their answers."""
    grouped: dict[tuple[str, tuple[str, ...]], list[LocatedRow]] = {}
    for row in rows:
        if (row.source, row.nr, row.page) in EXCLUDED_ROWS:
            continue
        grouped.setdefault(_group_key(row), []).append(row)

    questions: list[Question] = []
    conflicts: list[DedupConflict] = []

    for key, group in grouped.items():
        answer_by_class: dict[str, str] = {}
        rows_by_class: dict[str, list[LocatedRow]] = {}
        irreconcilable = False

        for source in sorted({row.source for row in group}):
            rows_of_class = [row for row in group if row.source == source]
            texts = set()
            for row in rows_of_class:
                index = _correct_index(row)
                if index is None:
                    irreconcilable = True
                    break
                texts.add(normalize_key(row.options[index]))
            if irreconcilable or len(texts) != 1:
                irreconcilable = True
                break
            answer_by_class[source] = texts.pop()
            rows_by_class[source] = rows_of_class

        if irreconcilable:
            texts = {
                normalize_key(row.options[index])
                for row in group
                if (index := _correct_index(row)) is not None
            }
            conflicts.append(
                DedupConflict(
                    key=key[0],
                    question=group[0].question,
                    correct_texts=tuple(sorted(texts)),
                )
            )
            continue

        if len(set(answer_by_class.values())) == 1:
            questions.append(_build(key, group, tuple(sorted(answer_by_class)), disputed=False))
        else:
            for source in sorted(rows_by_class):
                questions.append(_build(key, rows_by_class[source], (source,), disputed=True))

    return questions, conflicts
