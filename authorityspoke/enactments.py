from __future__ import annotations

import datetime
import pathlib
import re
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

from dataclasses import dataclass

from utils import roman

from authorityspoke.context import log_mentioned_context, get_directory_path


class Code:
    """
    A constitution, code of statutes, code of regulations,
    or collection of court rules.

    Each instance of this class depends on an XML file containing
    the code, so every new XML format will require adding a method
    to this class to ingest it.

    :param filename:
        the name of the file in the ``example_data/codes``
        folder where the XML version of the code can be found.
    """

    directory = get_directory_path("codes")

    def __init__(self, filename: str):
        self.path = self.__class__.directory / filename
        self.xml = self.get_xml()
        if filename.startswith("ca_"):
            self.title = self.xml.find("h3").find("b").text.split(" - ")[0]
            self.sovereign = "California"
        elif filename.startswith("usc"):
            self.title_number = int(self.xml.find("meta").find("docNumber").text)
            self.title = f"USC Title {self.title_number}"
            self.sovereign = "federal"
        elif filename.startswith("cfr"):
            self.title_number = int(self.xml.CFRGRANULE.FDSYS.CFRTITLE.text)
            self.title = f"Code of Federal Regulations Title {self.title_number}"
            self.sovereign = "federal"
        else:
            self.title = self.xml.find("dc:title").text
            if "United States" in self.title:
                self.sovereign = "federal"

        if "Constitution" in self.title:
            self.level = "constitutional"
        elif "Regulations" in self.title:
            self.level = "regulation"
        else:
            self.level = "statutory"

    def __str__(self):
        return self.title

    def get_xml(self):
        """
        :returns: the XML corresponding to this Code object.
        """
        with open(self.path) as fp:
            xml = BeautifulSoup(fp.read(), "lxml-xml")
        return xml

    def provision_effective_date(self, cite: str) -> datetime.date:
        """
        So far this method only covers the US Constitution and it
        assumes that the XML format is United States Legislative
        Markup (USLM).

        :param cite:
            a string representing the XML element name for the
            the legislative provision within this Code.

        :returns: the effective date of the cited provision
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


@dataclass(frozen=True)
class Enactment:

    """
    A passage of legislative text. May be used as support for a
    :class:`.ProceduralRule`. To retrieve the text, there needs
    to be an available method for identifying the correct XML
    element based on the section and subsection names, and each
    XML format used for a Code requires a different method.

    :param code:
        the :class:`Code` where this legislative text appears.

    :param section:
        identifier for the section of the :class:`Code` where
        the text can be found.

    :param subsection:
        identifier for the subsection of the :class:`Code` where
        the text can be found.

    :param start:
        a unique string corresponding to the first part of the
        quoted passage of legislative text

    :param end:
        a unique string corresponding to the end of the
        quoted passage of legislative text

    :param name:
        an identifier for this object, often used if the object needs
        to be referred to multiple times in the process of composing
        other :class:`Factor` objects.
    """
    code: Code
    section: str
    subsection: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    name: Optional[str] = None

    @property
    def effective_date(self):
        """
        :returns:
            the effective date of the text in this passage.
            Currently works only for the US Constitution.
        """
        return self.code.provision_effective_date(self.section)

    @property
    def text(self):
        """
        :returns: the full text of the cited passage from the XML.
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

        def usc_statute_text():
            section_identifier = f"/us/usc/t{self.code.title_number}/s{self.section}"
            section = self.code.xml.find(name="section", identifier=section_identifier)
            if self.subsection:
                subsection_identifier = f"{section_identifier}/{self.subsection}"
                section = section.find(
                    name="subsection", identifier=subsection_identifier
                )
            return section.find_all(["chapeau", "paragraph", "content"])

        if self.code.sovereign == "federal":
            if self.code.level == "regulation":
                passages = self.code.xml.find(
                    name="SECTNO", text=f"§ {202.1}"
                ).parent.find_all(name="P")
            elif hasattr(self.code, "title_number"):
                passages = usc_statute_text()
            else:
                passages = self.code.xml.find(id=self.section).find_all(name="text")
        elif self.code.sovereign == "California":
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

    def __str__(self):
        return f'"{self.text}" ({self.code.title}, {self.section})'

    def means(self, other: Enactment) -> bool:
        """
        It's questionable whether this comparison is really meaningful.
        You could always make the result ``False`` by comparing longer
        passages of text until you found a difference between the two
        sites in the text.

        :returns:
            whether ``self`` and ``other`` represent the same text
            issued by the same sovereign in the same level of
            :class:`Enactment`.
        """
        if not isinstance(other, self.__class__):
            return False

        return (
            self.text.strip(",:;. ") == other.text.strip(",:;. ")
            and self.code.sovereign == other.code.sovereign
            and self.code.level == other.code.level
        )

    def __ge__(self, other):
        """
        Why does this method not require the same ``code.sovereign`` and
        ``code.level``, especially considering that :meth:`means` does?

        :returns:
            Whether ``self`` "implies" ``other``, which in this context means
            whether ``self`` contains at least all the same text as ``other``.
        """

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + "implication with other Enactment objects."
            )

        return other.text.strip(",:;. ") in self.text

    def __gt__(self, other):
        if self == other:
            return False
        return self >= other

    @classmethod
    @log_mentioned_context
    def from_dict(
        cls, enactment_dict: Dict[str, str], mentioned: List[Dict[str, str]]
    ) -> Enactment:
        """
        No way to use an existing code object currently.
        Also, handing "mentioned" through this method is pointless.
        """
        code = Code(enactment_dict.get("code"))
        start = enactment_dict.get("start")
        end = enactment_dict.get("end")
        name = enactment_dict.get("name")
        text = enactment_dict.get("text")
        if text and not (start or end):
            start = text
            end = text

        return (
            Enactment(
                code=code,
                section=enactment_dict.get("section"),
                subsection=enactment_dict.get("subsection"),
                start=start,
                end=end,
                name=name,
            ),
            mentioned,
        )
