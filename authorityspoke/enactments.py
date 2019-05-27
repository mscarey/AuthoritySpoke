from __future__ import annotations

import datetime
import pathlib
import re
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

from lxml import etree

from utils import roman

from authorityspoke.context import log_mentioned_context, get_directory_path
from authorityspoke.selectors import TextQuoteSelector


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

    # namespaces for legislative XML schemas
    ns = {
        "uslm": "http://xml.house.gov/schemas/uslm/1.0",
        "dc": "http://purl.org/dc/elements/1.1/",
        "xhtml": "http://www.w3.org/1999/xhtml",
    }

    def __init__(self, filename: str):
        ns = self.__class__.ns
        self.filename = filename
        self.path = self.__class__.directory / filename
        with open(self.path) as fp:
            self.xml = etree.parse(fp)
        root = self.xml.getroot()
        if root.nsmap.get(None) == ns["uslm"]:
            title = self.xml.getroot().find("./uslm:main/uslm:title", ns)
            if title is not None:
                # The code is a USC title
                self.url = title.attrib["identifier"]
                self.title_number = int(
                    root.find("./uslm:meta/uslm:docNumber", ns).text
                )
                self.title = f"USC Title {self.title_number}"
            else:
                # The code is the US constitution
                self.url = "/us/const"
                self.title = root.find("./uslm:meta/dc:title", ns).text

        if filename.startswith("ca_"):
            self.url = "/us-ca"
            self.title = root.find(".//xhtml:h3/xhtml:b", ns).text.split(" - ")[0]
            if "Evidence" in self.title:
                self.url += "/evid"
            elif "Penal" in self.title:
                self.url += "/pen"

        elif filename.startswith("cfr"):
            self.title_number = int(root.xpath("/CFRGRANULE/FDSYS/CFRTITLE")[0].text)
            self.title = f"Code of Federal Regulations Title {self.title_number}"
            self.url = f"/us/cfr/t{self.title_number}"

        self.sovereign = self.url.split("/")[1]
        if "Constitution" in self.title:
            self.level = "constitutional"
        elif "Regulations" in self.title:
            self.level = "regulation"
        else:
            self.level = "statutory"

    @property
    def jurisdiction_id(self):
        return self.url.split("/")[1]

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

        if self.level == "constitutional" and self.sovereign == "us":
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

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.filename}")'

    def __str__(self):
        return self.title


@dataclass(frozen=True)
class Enactment:

    """
    A passage of legislative text. May be used as support for a
    :class:`.ProceduralRule`. To retrieve the text, there needs
    to be an available method for identifying the correct XML
    element based on the section and subsection names, and each
    XML format used for any :class:`Code` will require a different method.

    :param code:
        the :class:`Code` where this legislative text appears.

    :param selector:
        identifier for the place in the :class:`Code` where
        the text can be found.

    :param name:
        an identifier for this object, often used if the object needs
        to be referred to multiple times in the process of composing
        other :class:`.Factor` objects.
    """

    code: Code
    selector: TextQuoteSelector
    name: Optional[str] = None

    @property
    def effective_date(self):
        """
        :returns:
            the effective date of the text in this passage.
            Currently works only for the US Constitution.
        """
        return self.code.provision_effective_date(self.selector)

    @property
    def text(self):
        """
        :returns: the full text of the cited passage from the XML.
        """

        def cal_href(href):
            """
            Tests whether an XML element has an attribute labeling it as the text
            of the statutory section `self.section`.

            Uses `California statute XML format <http://leginfo.legislature.ca.gov/>`_.
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

        if self.code.sovereign == "us":
            if self.code.level == "regulation":
                passages = self.code.xml.find(
                    name="SECTNO", text=f"§ {202.1}"
                ).parent.find_all(name="P")
            elif self.code.url.split("/")[-1].startswith("t"):
                passages = usc_statute_text()
            else:
                passages = self.code.xml.find(id=self.section).find_all(name="text")
        elif self.code.sovereign == "us-ca":
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

    @classmethod
    @log_mentioned_context
    def from_dict(
        cls,
        enactment_dict: Dict[str, str],
        mentioned: Optional[List[Union["Factor", Enactment]]] = None,
        regime: Optional["Regime"] = None,
    ) -> Tuple[Enactment, Optional[List[Union[Enactment, Factor]]]]:
        """
        Creates a new :class:`Enactment` object using a :class:`dict`
        imported from JSON example data.

        There's currently no way to import an existing :class:`Code` object
        for use in composing the new :class:`Enactment`.

        :param enactment_dict:

        :param mentioned:
            not currently used, passed to the function to maintain
            symmetry with :meth:`.Function.from_dict`

        :param regime:
            the :class:`.Regime` where the :class:`.Code` that is the
            source for this `Enactment` can be found.
        """
        if regime is not None and regime.get_code(enactment_dict["path"]):
            code = regime.get_code(enactment_dict["path"])
        else:
            code = Code(enactment_dict["path"])
            if regime:
                regime.set_code(code)

        selector = TextQuoteSelector(
            path=enactment_dict.get("path"),
            exact=enactment_dict.get("exact"),
            prefix=enactment_dict.get("prefix"),
            suffix=enactment_dict.get("suffix"),
        )

        return (
            Enactment(code=code, selector=selector, name=enactment_dict.get("name")),
            mentioned,
        )

    def means(self, other: Enactment) -> bool:
        """
        Whether the meaning of ``self`` is equivalent to (neither
        broader nor narrower than) the meaning of the legislative
        text passage ``other``.

        .. note::
            You could always make the result ``False`` by comparing longer
            passages of text until you found a difference between the two
            sites in the text. Does this undercut the usefulness of the
            ``means`` method?

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

    def __str__(self):
        return f'"{self.text}" ({self.code.title}, {self.section})'

    def __ge__(self, other):
        """
        .. note::
            Why does this method not require the same ``code.sovereign``
            and ``code.level``, especially considering that
            :meth:`means` does?

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
