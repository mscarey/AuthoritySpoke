from __future__ import annotations

import datetime
import functools
import pathlib
import re
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

from bs4 import BeautifulSoup

from utils import roman

from authorityspoke.context import log_mentioned_context, get_directory_path
from authorityspoke.selectors import TextQuoteSelector
from utils.cache import lazyprop


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
        self.filename = filename

    @property
    def path(self):
        """
        :returns:
            The path to the file where the XML file for
            the code can be found.
        """
        return self.__class__.directory / self.filename

    @lazyprop
    def jurisdiction(self) -> str:
        """
        :returns:
            The abbreviation for the jurisdiction that
            enacted the ``Code``, in USLM-like format.

            e.g. ``us`` for U.S. federal laws,
            ``us-ca`` for California state laws.
        """
        return self.uri.split("/")[1]

    @property
    def level(self) -> str:
        """
        :returns:
            "constitution", "statute", or "regulation"
        """

        if "Constitution" in self.title:
            return "constitution"
        elif "Regulations" in self.title:
            return "regulation"
        else:
            return "statute"

    @lazyprop
    def title(self) -> str:
        """
        :returns:
            the contents of an XML ``title`` element that
            describes the ``Code``, if any. Otherwise
            returns a descriptive name that may not exactly
            appear in the XML.
        """

        uslm_title = self.xml.find("dc:title")
        if uslm_title:
            return uslm_title.text
        cal_title = self.xml.h3
        if cal_title:
            code_name = cal_title.b.text.split(" - ")[0]
            return f"California {code_name}"
        cfr_title = self.xml.CFRGRANULE.FDSYS.CFRTITLE
        if cfr_title:
            return f"Code of Federal Regulations Title {cfr_title.text}"
        raise NotImplementedError

    @lazyprop
    def uri(self) -> str:
        """
        .. note::
            This handles California state statutes only with a
            mockup, which can only refer to the Penal and Evidence
            Codes.

        :returns:
            The `United States Legislative Markup (USLM)
            <https://github.com/usgpo/uslm>`_ identifier that
            describes the document as a whole, if available in
            the XML. Otherwise returns a pseudo-USLM identifier.
        """
        title = self.title
        if title == "Constitution of the United States":
            return "/us/const"
        if title.startswith("Title"):
            return self.xml.find("main").find("title")["identifier"]
        if title.startswith("California"):
            uri = "/us-ca/"
            if "Penal" in title:
                return uri + "pen"
            else:
                return uri + "evid"
        if title.startswith("Code of Federal Regulations"):
            title_num = title.split()[-1]
            return f"/us/cfr/t{title_num}"
        raise NotImplementedError

    @lazyprop
    def xml(self):
        """
        :returns:
            A BeautifulSoup object created by parsing the
            ``Code``\'s XML file
        """
        with open(self.path) as fp:
            xml = BeautifulSoup(fp, "lxml-xml")
        return xml

    def format_uri_for_const(self, uri: str) -> str:
        """
        Although the US Constitution is published in a format
        described as USML, its section identifier strings differ from
        those in USC USML documents in that they skip the jurisdiction
        and code fields, skip the initial slash character,
        start with the section field, and convert all remaining
        slashes to hyphens.

        This will only remove the path to the current code if
        the current code is the same one referenced in the URI.
        So the example below assumes the current ``Code`` object
        has ``self.uri == "/us/const"``

        :param uri:
            an identifier in a format consistent with USC USML
            documents, e.g. ``/us/const/amendment/XIV/1``

        returns
            an identifier in a format found in the USLM version of
            the federal constitution, e.g. ``amendment-XIV-1``
        """
        return uri.replace(self.uri, "").lstrip("/").replace("/", "-")

    def provision_effective_date(
        self, cite: Union[TextQuoteSelector, str]
    ) -> datetime.date:
        """
        So far this method only covers the US Constitution and it
        assumes that the XML format is `United States Legislative
        Markup (USLM) <https://github.com/usgpo/uslm>`_.

        :param cite:
            a string or selector representing the XML element name for the
            the legislative provision within this ``Code``.

        :returns:
            the effective date of the cited provision
        """

        if isinstance(cite, TextQuoteSelector):
            cite = cite.path
        if self.level == "constitution" and self.jurisdiction == "us":
            cite = self.format_uri_for_const(cite)
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

        raise NotImplementedError

    def select_text(self, selector: TextQuoteSelector) -> str:
        """
        :param selector:
            a selector referencing a text passage in the ``Code``.

        .. note::
            When handling Code of Federal Regulation (CFR) :class:`.Enactment`\s,
            this can only select from the whole document or from Sections,
            not Subsections or any other level. Still hoping to be able
            to switch to a `United States Legislative Markup (USLM)
            <https://github.com/usgpo/uslm>`_-like XML format for CFR.

        :returns:
            the text referenced by the selector.
        """

        def cal_href(href, docpath):
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

        if selector.path is not None:
            docpath = selector.path.replace(self.uri, "")
        else:
            passages = self.xml.find_all(name="text")

        if self.jurisdiction == "us":
            if self.level == "regulation":
                section = docpath.split("/")[1]
                passages = self.xml.find(
                    name="SECTNO", text=f"§ {section}"
                ).parent.find_all(name="P")
            elif docpath.split("/")[1].startswith("t"):
                passages = usc_statute_text()
            else:  # federal constitution
                passages = self.xml.find(id=docpath.split("/")[1]).find_all(name="text")

        elif self.jurisdiction == "us-ca":
            passages = self.xml.find(href=cal_href).parent.find_next_siblings(
                style="margin:0;display:inline;"
            )

        text = "".join(passage.text for passage in passages)
        text = re.sub(r"\s+", " ", text).strip()
        return text

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

        return self.code.select_text(self.selector)

    @classmethod
    @log_mentioned_context
    def from_dict(
        cls, enactment_dict: Dict[str, str], regime: Optional["Regime"] = None
    ) -> Tuple[Enactment, Optional[List[Union[Enactment, Factor]]]]:
        """
        Creates a new :class:`Enactment` object using a :class:`dict`
        imported from JSON example data.

        There's currently no way to import an existing :class:`Code` object
        for use in composing the new :class:`Enactment`.

        :param enactment_dict:

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

        selector = TextQuoteSelector(**enactment_dict, code=code)

        return Enactment(code=code, selector=selector, name=enactment_dict.get("name"))

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
