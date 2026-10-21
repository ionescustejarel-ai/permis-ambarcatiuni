"""What the three catalogues now share, tested once instead of three times."""

import pytest

from caa.catalogue import announcing, index_by_source, orphan_sources, resolve

ENTRIES = [
    ("alfa", ("Un text.", "Alt text al lui alfa.")),
    ("beta", ("Textul lui beta.",)),
]


def test_every_quote_of_every_entry_reaches_the_index():
    index = index_by_source(ENTRIES)
    assert set(index.values()) == {"alfa", "beta"}
    assert len(index) == 3


def test_the_index_compares_without_diacritics_or_punctuation():
    index = index_by_source([("alfa", ("Lumină verde, din tribord!",))])
    assert resolve(index, [("q1", "LUMINA  VERDE din TRIBORD")]) == {"q1": "alfa"}


def test_a_field_that_merely_contains_a_quote_is_a_different_field():
    """Fragment matching would put a neighbouring question under the wrong entry."""
    index = index_by_source(ENTRIES)
    assert resolve(index, [("q1", "Un text. Și încă ceva.")]) == {}


def test_a_catalogue_may_pass_one_field_or_two():
    index = index_by_source(ENTRIES)
    # Sound patterns live only in the answer; marks and arcs in either field.
    assert resolve(index, [("q1", "Un text.")]) == {"q1": "alfa"}
    assert resolve(index, [("q2", "nimic", "Textul lui beta.")]) == {"q2": "beta"}


def test_two_fields_naming_the_same_entry_are_not_a_conflict():
    index = index_by_source(ENTRIES)
    assert resolve(index, [("q1", "Un text.", "Alt text al lui alfa.")]) == {"q1": "alfa"}


def test_two_fields_naming_different_entries_raise():
    """Taking whichever was tried first is not a policy; the loser would vanish."""
    index = index_by_source(ENTRIES)
    with pytest.raises(ValueError, match="alfa.*beta"):
        resolve(index, [("q1", "Un text.", "Textul lui beta.")])


def test_a_quote_the_bank_no_longer_holds_is_reported_with_its_entry():
    orphans = orphan_sources(ENTRIES, ["Un text.", "Alt text al lui alfa."])
    assert orphans == [("beta", "Textul lui beta.")]


def test_nothing_is_orphaned_when_every_quote_is_present():
    texts = [source for _, sources in ENTRIES for source in sources]
    assert orphan_sources(ENTRIES, texts) == []


def test_only_the_fields_that_announce_are_offered_for_the_finding():
    """The finding must name a field that describes the thing, not its neighbour."""
    announces = lambda text: "arc" in text
    assert announcing(("un arc de 90°", "aproximativ 1 secunda"), announces) == ["un arc de 90°"]
    assert announcing(("aproximativ 1 secunda", "b"), announces) == []
