import json
import re

import pytest

from authorityspoke.textselectors.selectors import TextQuoteSelector
from authorityspoke.textselectors.selectors import TextPositionSelector


class TestQuoteSelectors:
    preexisting_material = TextQuoteSelector(
        exact=(
            "protection for a work employing preexisting material in which "
            + "copyright subsists does not extend to any part of the work in "
            + "which such material has been used unlawfully."
        )
    )

    in_no_case = TextQuoteSelector(suffix="idea, procedure,")

    copyright_requires_originality = TextQuoteSelector(suffix="fixed in any tangible")

    s102b = (
        "In no case does copyright protection for an original "
        + "work of authorship extend to any idea, procedure, process, system, "
        + "method of operation, concept, principle, or discovery, regardless of "
        + "the form in which it is described, explained, illustrated, or "
        + "embodied in such work."
    )

    amendment = (
        "All persons born or naturalized in the United States "
        "and subject to the jurisdiction thereof, are citizens "
        "of the United States and of the State wherein they reside. "
        "No State shall make or enforce any law which shall abridge "
        "the privileges or immunities of citizens of the United States; "
        "nor shall any State deprive any person of life, liberty, or "
        "property, without due process of law; nor deny to any person "
        "within its jurisdiction the equal protection of the laws."
    )

    amendment_selector = TextQuoteSelector(
        exact="",
        prefix="immunities of citizens of the United States; ",
        suffix=" nor deny to any person",
    )

    def test_convert_selector_to_json(self):
        copyright_dict = self.preexisting_material.dump()
        assert '"exact": "protection for a work' in json.dumps(copyright_dict)

    def test_failed_prefix(self):
        """
        The phrase "sound recordings" is not in
        the cited subsection, so searching for the interval will fail.
        """
        after_sound = TextQuoteSelector(prefix="sound recordings")
        assert after_sound.as_position(self.s102b) is None

    def test_failed_suffix(self):
        up_to_sound = TextQuoteSelector(suffix="sound recordings")
        assert up_to_sound.as_position(self.s102b) is None

    def test_interval_from_just_prefix(self):
        """
        The interval should be from the end of the prefix to the end of the
        text passage.

        141 means the string starts at the beginning of a word.
        If it started with 140, there would be a leading space.
        """
        selector = TextQuoteSelector(prefix="method of operation,")
        assert selector.as_position(self.s102b) == TextPositionSelector(
            141, len(self.s102b)
        )

    def test_exact_from_just_suffix(self):
        exact = self.in_no_case.select_text(self.s102b)
        assert exact == (
            "In no case does copyright protection for an original "
            + "work of authorship extend to any"
        )

    def test_exact_from_prefix_and_suffix(self):
        exact = self.amendment_selector.select_text(self.amendment)
        assert exact.startswith("nor shall any State deprive")

    def test_select_text(self):
        selector = TextQuoteSelector(
            prefix="in no case", exact="does copyright", suffix="protection"
        )
        assert selector.select_text(self.s102b) == "does copyright"

    def test_select_text_without_exact(self):
        selector = TextQuoteSelector(prefix="in no case", suffix="protection")
        assert selector.select_text(self.s102b) == "does copyright"

    def test_rebuilding_from_text(self):
        new_selector = self.amendment_selector.rebuild_from_text(self.amendment)
        assert new_selector.exact.startswith("nor shall any State deprive")

    def test_failing_to_rebuild_from_text(self):
        new_selector = self.amendment_selector.rebuild_from_text(
            "does not contain selected passages"
        )
        assert not new_selector

    def test_make_position_selector(self):
        new_selector = self.amendment_selector.as_position(self.amendment)
        assert new_selector.start == self.amendment.find("nor shall any State")

    def test_failing_to_make_position_selector(self):
        new_selector = self.amendment_selector.as_position(
            "does not contain selected passages"
        )
        assert not new_selector

    def test_regex_from_selector_with_just_exact(self):
        selector = TextQuoteSelector(exact="nor shall any State")
        assert selector.passage_regex_without_exact() == r"^.*$"
        assert selector.passage_regex() == r"(nor\ shall\ any\ State)"

    def test_selector_escapes_special_characters(self):
        selector = TextQuoteSelector(suffix="opened the C:\documents folder")
        pattern = selector.passage_regex()
        match = re.match(pattern, "Lee \n opened the C:\documents folder yesterday")
        assert match

    def test_regex_match(self):
        """
        Comparable to how TextQuoteSelector.exact_from_ends works.

        Provided because double-escaping makes it confusing
        to understand regex patterns constructed by Python.
        """
        pattern = (
            r"immunities\ of\ citizens\ of\ the\ United\ States;"
            + r"\s*(.*?)\s*nor\ deny\ to\ any\ person"
        )
        match = re.search(pattern, self.amendment)
        assert (
            match.group(1)
            == "nor shall any State deprive any person of life, liberty, or property, without due process of law;"
        )

    # TextPositionSelectors

    def test_add_position_selectors(self):
        left = TextPositionSelector(start=5, end=22)
        right = TextPositionSelector(start=12, end=27)
        new = left + right
        assert new.start == 5
        assert new.end == 27

    def test_add_nearly_overlapping_selectors(self):
        left = TextPositionSelector(start=5, end=22)
        right = TextPositionSelector(start=24, end=27)
        new = left + right
        assert new.start == 5
        assert new.end == 27

    def test_adding_nonoverlapping_selectors(self):
        """
        When the selectors aren't near enough to be added,
        the operation returns the selector on the left side.
        """
        left = TextPositionSelector(start=5, end=12)
        right = TextPositionSelector(start=24, end=27)
        new = left + right
        assert new is None

    def test_fail_combining_with_short_text(self):
        left = TextPositionSelector(start=5, end=12)
        right = TextPositionSelector(start=10, end=27)
        text = "This is 26 characters long"
        with pytest.raises(ValueError):
            _ = left.combine(other=right, text=text)

    def test_combine_with_text(self):
        left = TextPositionSelector(start=5, end=12)
        right = TextPositionSelector(start=10, end=26)
        text = "This is 26 characters long"
        new = left.combine(other=right, text=text)
        assert new.end == 26

    def test_dump_position_selector(self):
        selector = TextPositionSelector(start=5, end=12)
        dumped = selector.dump()
        assert dumped["type"] == "TextPositionSelector"

    def test_get_passage_from_position(self):
        selector = TextPositionSelector(start=53, end=84)
        passage = selector.passage(self.amendment)
        assert passage == "and subject to the jurisdiction"

    def test_fail_to_get_passage_from_position(self):
        selector = TextPositionSelector(start=53, end=9984)
        with pytest.raises(ValueError):
            _ = selector.passage(self.amendment)

    def test_end_must_be_after_start_position(self):
        with pytest.raises(ValueError):
            _ = TextPositionSelector(start=53, end=14)

    def test_min_start_position_is_0(self):
        selector = TextPositionSelector(start=-3, end=84)
        assert selector.start == 0
