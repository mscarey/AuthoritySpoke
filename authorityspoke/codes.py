"""Classes representing legislation."""

from __future__ import annotations

import datetime
import functools
import re
from typing import List, Optional, Sequence, Tuple, Union

from anchorpoint.textselectors import TextQuoteSelector, TextPositionSelector
from bs4 import BeautifulSoup

from authorityspoke.utils.roman import from_roman


class Code:
    r"""
    A code of legislation.

    Could be a constitution, code of statutes, code of regulations,
    or collection of court rules.

    Each instance of this class depends on an XML file containing
    the code, so every new XML format will require adding a method
    to this class to ingest it.

    :param xml:
        A BeautifulSoup object created by parsing the
        ``Code``\'s XML file

    :param title:
        A name for the :class:`Code` that may have been found in
        an XML ``title`` element. For larger codes like the United
        States Code, this should identify the title number, and the
        :class:`Code` object will contain text only from that title.

    :param uri:
        The `United States Legislative Markup (USLM)
        <https://github.com/usgpo/uslm>`_ identifier that
        describes the document as a whole, if available.
        Otherwise, should be a pseudo-USLM identifier.
    """

    # namespaces for legislative XML schemas
    ns = {
        "uslm": "http://xml.house.gov/schemas/uslm/1.0",
        "dc": "http://purl.org/dc/elements/1.1/",
        "xhtml": "http://www.w3.org/1999/xhtml",
    }

    def __init__(self, xml, title: str, uri: str):
        """Link an entire XML tree to the Code."""
        self.xml = xml
        self.title = title
        self.uri = uri

    @property
    def jurisdiction(self) -> str:
        """
        Get string representing the jurisdiction from within ``uri``.

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
        Get level of legislation for this Code, e.g. "statute".

        :returns:
            "constitution", "statute", or "regulation"
        """
        if "Constitution" in self.title:
            return "constitution"
        elif "Regulations" in self.title:
            return "regulation"
        return "statute"

    def text_interval(
        self, selector: Optional[TextQuoteSelector] = None, path: str = ""
    ) -> Optional[TextPositionSelector]:
        """
        Find integer indices for the quoted text.

        :returns:
            A :class:`TextPositionSelector` containing the lower and upper bounds of the
            text passage quoted in ``self.selector.exact`` within the
            XML section referenced in ``self.selector.path``.
        """
        sections = self.get_sections(path)
        if not sections:
            raise ValueError(f"Section {path} does not exist in code {self.title}")

        text = self.section_text(sections)
        if not selector:
            return (0, len(text))
        return selector.as_position(text)

    def provision_effective_date(self, cite: str) -> datetime.date:
        """Give effective date for a provision within the Code."""
        raise NotImplementedError

    def get_exact_from_source(
        self, source: str, selector: TextQuoteSelector
    ) -> Optional[str]:
        """
        Use ``source`` to find text for ``exact`` parameter.

        :param source:
            path to a cited section or node, which may contain subsections

        :param selector:
            selector for the cited text passage within the cited node
        """

        sections = self.get_sections(source)
        section_text = self.section_text(sections)
        return selector.select_text(section_text)

    def make_docpath(self, path: str = "") -> str:
        """Remove Code identifier from path to get a path relative to the document."""
        docpath = path or self.uri
        if not docpath.startswith(self.uri):
            return docpath  # path could be relative to the Code already
        return docpath.replace(self.uri, "")

    def _get_sections_from_relative_path(self, docpath: str) -> Optional[BeautifulSoup]:
        """
        Get sections using relative path, assuming Code follows USLM standard.
        """
        passage_nodes = ["chapeau", "paragraph", "content", "continuation"]
        if docpath.endswith(("chapeau", "continuation")):
            docpath, suffix = docpath.rsplit("/", maxsplit=1)
            passage_nodes = [suffix]
        sections = self.xml.find(identifier=docpath)
        if not sections:
            return None
        passages = sections.find_all(passage_nodes)

        return passages

    def get_sections(self, path: str = "") -> Optional[BeautifulSoup]:
        r"""
        Get sections identified by a path, if present in the :class:`Code`\.

        :param path:
            a path string, in the format used for :class:`.Enactment`
            objects, to the section with the text to be returned.

        :returns:
            the text of a section of the :class:`Code`.
        """
        docpath = self.make_docpath(path)
        if not docpath:  # selecting the whole Code
            return self.xml.find_all(name="text")
        return self._get_sections_from_relative_path(docpath)

    @staticmethod
    def section_text(passages: Sequence[BeautifulSoup]) -> str:
        """
        Get the text of legislative sections from XML elements.

        :param passages:
            a sequence of XML elements with text to join

        :returns:
            the text of the XML elements.
        """

        return " ".join(" ".join(passage.text.split()) for passage in passages)

    def section_text_from_path(self, path: str = "") -> str:
        """
        Get the text of legislative sections from a path identifier.

        :param path:
            a path string, in the format used for :class:`.Enactment`
            objects, to the section with the text to be returned.

        :returns:
            the text of the XML elements.
        """
        sections = self.get_sections(path)
        return self.section_text(sections)

    def select_text_from_interval(
        self, interval: TextPositionSelector, path: Optional[str] = None,
    ) -> Optional[str]:
        """
        Select text as interval of section identified by path.

        If ``path`` parameter is not given, selects an interval from the
        whole :class:`Code`.

        :param interval:
            the indices of the slice of the section text to be selected.

        :para path:
            a path to the section that text should be selected from

        :returns:
            a slice of text from the section identified by ``path``
        """
        sections = self.get_sections(path)
        if not sections:
            raise ValueError(f"Section {path} does not exist in {self}.")
        section_text = self.section_text(sections)
        return interval.passage(section_text)

    def select_text(
        self, path: Optional[str], selector: Optional[TextQuoteSelector] = None
    ) -> Optional[str]:
        r"""
        Get text from the ``Code`` using a :class:`.TextQuoteSelector`.

        :param selector:
            a selector referencing a text passage in the ``Code``.

        .. note::
            When handling Code of Federal Regulation (CFR) :class:`.Enactment`\s,
            this can only select from the whole document or from Sections,
            not Subsections or any other level. Still hoping to be able
            to switch to a `United States Legislative Markup (USLM)
            <https://github.com/usgpo/uslm>`_-like XML format for CFR.

        :returns:
            the text referenced by the selector, or ``None`` if the text
            can't be found.
        """
        sections = self.get_sections(path)
        text = self.section_text(sections)
        if not selector:
            return text
        return selector.select_text(text)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.title})"

    def __str__(self):
        return self.title


class USConstCode(Code):
    def format_uri_for_const(self, uri: str) -> str:
        """
        Convert ``uri`` to identifier for constitution sections.

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

        :returns:
            an identifier in a format found in the USLM version of
            the federal constitution, e.g. ``amendment-XIV-1``
        """
        return uri.replace(self.uri, "").lstrip("/").replace("/", "-")

    def get_fed_const_section(self, path: str) -> BeautifulSoup:
        """
        Get a section from a USLM identifier if ``self`` is the US Constitution.

        :param path:
            a USLM path to a section of the US Constitution, with or
            without the part that identifies the :class:`Code`, but without
            a namespace declaration.

        :returns:
            the XML section of ``self`` matching the path.
        """
        path = self.format_uri_for_const(path)
        path_parts: List[str] = []
        for _ in range(path.count("/") + 1):
            path_parts.append(path[: (path.index("/") if "/" in path else None)])
            path = path.replace("/", "-", 1)
        section = self.xml
        for part in path_parts:
            section = section.find(id=part)
        return section

    def _get_sections_from_relative_path(self, docpath: str) -> Optional[BeautifulSoup]:

        cited_section = self.get_fed_const_section(docpath)
        passages = cited_section.find_all(name="text")

        return passages

    def provision_effective_date(self, cite: str) -> datetime.date:
        """
        Give effective date for a provision within the Code.

        So far this method only covers the US Constitution and it
        assumes that the XML format is `United States Legislative
        Markup (USLM) <https://github.com/usgpo/uslm>`_.

        :param cite:
            a string or selector representing the XML element name for the
            the legislative provision within this ``Code``.

        :returns:
            the effective date of the cited provision
        """
        cite = self.format_uri_for_const(cite)
        if "amendment" not in cite.lower():
            return datetime.date(1788, 9, 13)
        roman_numeral = cite.split("-")[1]
        amendment_number = from_roman(roman_numeral)
        if amendment_number < 11:
            return datetime.date(1791, 12, 15)
        section = self.xml.find(id=cite)
        if section.name == "level":
            enactment_text = section.find("note").p.text
        else:
            enactment_text = section.parent.find("note").p.text
        month_first = re.compile(
            r"(?:Secretary of State|Administrator of General Services|certificate of the Archivist)"
            r"(?: accordingly issued a proclamation)?,? dated (\w+ \d\d?, \d{4}),"
        )
        day_first = re.compile(
            r"(?:Congress|Secretary of State),? dated the (\d\d?th of \w+, \d{4}),"
        )
        result = month_first.search(enactment_text)
        if result:
            return datetime.datetime.strptime(result.group(1), "%B %d, %Y").date()
        result = day_first.search(enactment_text)
        return datetime.datetime.strptime(result.group(1), "%dth of %B, %Y").date()


class USLMCode(Code):
    def make_docpath(self, path: str = "") -> str:
        """
        Don't remove Code uri from path because USC uses full paths as identifiers.
        """
        return path.rstrip("/") or self.uri


class USCCode(USLMCode):
    def __str__(self):
        return f"USC {self.title}"


class CFRCode(Code):
    def _get_sections_from_relative_path(self, docpath: str) -> Optional[BeautifulSoup]:

        section = docpath.split("/")[1].strip("s")
        citation = self.xml.find(name="SECTNO", text=f"§ {section}")
        if not citation:
            return None
        return citation.parent.find_all(name="P")


class CalCode(Code):
    def _get_sections_from_relative_path(self, docpath: str) -> Optional[BeautifulSoup]:
        def cal_href(docpath, href):
            """
            Test if XML element is labeled as the text of the section in ``docpath``.

            Uses `California statute XML format <http://leginfo.legislature.ca.gov/>`_.
            """
            section = docpath.split("/")[1].strip("s")
            return href and re.compile(
                r"^javascript:submitCodesValues\('" + section
            ).search(href)

        this_cal_section = functools.partial(cal_href, docpath)
        passages = self.xml.find(href=this_cal_section).parent.find_next_siblings(
            style="margin:0;display:inline;"
        )
        return passages
