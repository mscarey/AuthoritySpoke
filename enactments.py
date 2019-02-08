import datetime
import pathlib
import re
from typing import Dict, Optional

from bs4 import BeautifulSoup

import roman


class Code:
    """
    A constitution, code of statutes, code of regulations,
    or collection of court rules.
    """

    def __init__(self, filename: str):
        self.path = pathlib.Path("codes") / filename
        self.xml = self.get_xml()
        if filename.startswith("ca_"):
            self.title = self.xml.find("h3").find("b").text.split(" - ")[0]
            self.sovereign = "California"
        else:
            self.title = self.xml.find("dc:title").text
            if "United States" in self.title:
                self.sovereign = "federal"

        if "Constitution" in self.title:
            self.level = "constitutional"
        else:
            self.level = "statutory"

    def __str__(self):
        return self.title

    def get_xml(self):
        with open(self.path) as fp:
            xml = BeautifulSoup(fp.read(), "lxml-xml")
        return xml

    def provision_effective_date(self, cite):
        """
        Given the "citation" of a legislative provision
        (only XML element names are used as citations so far),
        retrieves the effective date of the provision from
        the United States Legislative Markup (USLM) XML version
        of the code where the provision is located.

        So far this only covers the US Constitution.
        """

        if self.level == "constitutional" and self.sovereign == "federal":
            if "amendment" not in cite.lower():
                return datetime.date(1788, 9, 13)
            roman_numeral = cite.split("-")[1]
            amendment_number = roman.from_roman(roman_numeral)
            if amendment_number < 11:
                return datetime.date(1791, 12, 15)
            section = self.xml.find(id=cite)
            if section.name == "level":
                enactment_text = section.find("note").p.text
            else:
                enactment_text = section.parent.find("note").p.text
            month_first = re.compile(
                r"""(?:Secretary of State|Administrator of General Services|certificate of the Archivist)(?: accordingly issued a proclamation)?,? dated (\w+ \d\d?, \d{4}),"""
            )
            day_first = re.compile(
                r"(?:Congress|Secretary of State),? dated the (\d\d?th of \w+, \d{4}),"
            )
            result = month_first.search(enactment_text)
            if result:
                return datetime.datetime.strptime(result.group(1), "%B %d, %Y").date()
            result = day_first.search(enactment_text)
            return datetime.datetime.strptime(result.group(1), "%dth of %B, %Y").date()

        return NotImplementedError


class Enactment:
    def __init__(
        self,
        code: Code,
        section: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ):
        self.code = code
        self.section = section
        self.start = start
        self.end = end

        self.text = self.get_cited_passage()

        self.effective_date = self.code.provision_effective_date(section)

    def get_cited_passage(self):

        """
        Given the attributes describing the section and the start and end points
        of the cited text, collects the full text of the cited passage from the XML.
        """

        def cal_href(href):
            """
            Tests whether an XML element has an attribute labeling it as the text
            of the statutory section "self.section".

            Uses the California statute XML format from http://leginfo.legislature.ca.gov/.
            """

            return href and re.compile(
                r"^javascript:submitCodesValues\('" + self.section
            ).search(href)

        if self.code.sovereign == "federal":
            passages = self.code.xml.find(id=self.section).find_all(name="text")
        if self.code.sovereign == "California":
            passages = self.code.xml.find(href=cal_href).parent.find_next_siblings(
                style="margin:0;display:inline;"
            )

        text = "".join(passage.text for passage in passages)
        text = re.sub(r"\s+", " ", text).strip()
        if self.start:
            l = text.find(self.start)
        else:
            l = 0
        if self.end:
            r = text.find(self.end) + len(self.end)
        else:
            r = len(text)
        return text[l:r]

    def __hash__(self):
        return hash((self.text, self.code.sovereign, self.code.level))

    def __str__(self):
        return f'"{self.text}" ({self.code.title}, {self.section})'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (
            self.text.strip(",:;. ") == other.text.strip(",:;. ")
            and self.code.sovereign == other.code.sovereign
            and self.code.level == other.code.level
        )

    def __ge__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return other.text.strip(",:;. ") in self.text

    def __gt__(self, other):
        if self == other:
            return False
        return self >= other

    def from_dict(enactment_dict: Dict[str, Optional[str]]) -> "Enactment":
        code = Code(enactment_dict.get("code", None))
        return Enactment(
            code=code,
            section=enactment_dict.get("section", None),
            start=enactment_dict.get("start", None),
            end=enactment_dict.get("end", None),
        )
