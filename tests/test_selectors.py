import json

import pytest

from authorityspoke.textselectors.selectors import TextQuoteSelector
from authorityspoke.textselectors.selectors import TextPositionSelector

class TestQuoteSelectors:
    preexisting_material = TextQuoteSelector(
            exact=(
                "protection for a work employing preexisting material in which "
                + "copyright subsists does not extend to any part of the work in "
                + "which such material has been used unlawfully."
            ))
    copyright = TextQuoteSelector(suffix="idea, procedure,")
    copyright_requires_originality = TextQuoteSelector(
            suffix="fixed in any tangible"
        )
    s102b = (
        "In no case does copyright protection for an original " +
        "work of authorship extend to any idea, procedure, process, system, " +
        "method of operation, concept, principle, or discovery, regardless of " +
        "the form in which it is described, explained, illustrated, or " +
        "embodied in such work.")
    
    def test_convert_selector_to_json(self):
        copyright_dict = self.preexisting_material.dump()
        assert '"exact": "protection for a work' in json.dumps(copyright_dict)

    def test_failed_prefix(self):
        """
        The phrase "sound recordings" is not in
        the cited subsection, so searching for the interval will fail.
        """
        after_sound = TextQuoteSelector(prefix="sound recordings")
        assert after_sound.get_interval(self.s102b) is None

    def test_failed_suffix(self):
        up_to_sound = TextQuoteSelector(suffix="sound recordings")
        assert up_to_sound.get_interval(self.s102b) is None

    def test_interval_from_just_prefix(self):
        """
        The interval should be from the end of the prefix to the end of the
        text passage.

        141 means the string starts at the beginning of a word.
        If it started with 140, there would be a leading space.
        """
        selector = TextQuoteSelector(prefix="method of operation,")
        assert selector.get_interval(self.s102b) == (141, len(self.s102b))


