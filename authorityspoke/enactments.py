"""Classes representing legislation."""

from __future__ import annotations

import datetime
import functools
import pathlib
import re
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass

from bs4 import BeautifulSoup

from utils.cache import lazyprop
from utils.roman import from_roman

from authorityspoke.selectors import TextQuoteSelector


class Code:
    r"""
    A code of legislation.

    Could be a constitution, code of statutes, code of regulations,
    or collection of court rules.

    Each instance of this class depends on an XML file containing
    the code, so every new XML format will require adding a method
    to this class to ingest it.

    :param filepath:
        the name of the file in the ``example_data/codes``
        folder where the XML version of the code can be found.
    """

    # namespaces for legislative XML schemas
    ns = {
        "uslm": "http://xml.house.gov/schemas/uslm/1.0",
        "dc": "http://purl.org/dc/elements/1.1/",
        "xhtml": "http://www.w3.org/1999/xhtml",
    }

    def __init__(self, filepath: pathlib.Path):
        """Set ``filepath`` parameter as attribute."""
        self.filepath = filepath

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
        Get identifier for the :class:`.Enactment` type found in this ``Code``.

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
        Provide "title" identifier for the ``Code``'s XML.

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
        Build a URI for the ``Code`` based on its XML metadata.

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
        Get XML tree of legislative provisions.

        :returns:
            A BeautifulSoup object created by parsing the
            ``Code``\'s XML file
        """
        with open(self.filepath) as fp:
            xml = BeautifulSoup(fp, "lxml-xml")
        return xml

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

    def provision_effective_date(
        self, cite: Union[TextQuoteSelector, str]
    ) -> datetime.date:
        """
        Give effective date for a provision within the ``Code``.

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
            amendment_number = from_roman(roman_numeral)
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
        path = path.replace(self.uri, "")
        path_parts: List[str] = []
        path = path.lstrip("/")
        for _ in range(path.count("/") + 1):
            path_parts.append(path[: (path.index("/") if "/" in path else None)])
            path = path.replace("/", "-", 1)
        section = self.xml
        for part in path_parts:
            section = section.find(id=part)
        return section

    @functools.lru_cache()
    def section_text(self, path: str) -> str:
        """
        Get the text of the section identified by a path.

        :param path:
            a path string, in the format used for :class:`.TextQuoteSelector`
            objects, to the section with the text to be returned.

        :returns:
            the text of a section of the :class:`Code`.
        """

        def cal_href(docpath, href):
            """
            Test if XML element is labeled as the text of the section in ``docpath``.

            Uses `California statute XML format <http://leginfo.legislature.ca.gov/>`_.
            """
            section = docpath.split("/")[1].strip("s")
            return href and re.compile(
                r"^javascript:submitCodesValues\('" + section
            ).search(href)

        def usc_statute_text():
            section = self.xml.find(identifier=path)
            return section.find_all(["chapeau", "paragraph", "content"])

        if path is not None:
            docpath = path.replace(self.uri, "")

        if not docpath:  # selecting the whole Code
            passages = self.xml.find_all(name="text")
        elif self.jurisdiction == "us":
            if self.level == "regulation":
                section = docpath.split("/")[1].strip("s")
                passages = self.xml.find(
                    name="SECTNO", text=f"§ {section}"
                ).parent.find_all(name="P")
            elif self.level == "statute":
                passages = usc_statute_text()
            else:  # federal constitution
                cited_section = self.get_fed_const_section(docpath)
                passages = cited_section.find_all(name="text")

        elif self.jurisdiction == "us-ca":
            this_cal_section = functools.partial(cal_href, docpath)
            passages = self.xml.find(href=this_cal_section).parent.find_next_siblings(
                style="margin:0;display:inline;"
            )

        return " ".join(" ".join(passage.text.split()) for passage in passages)

    def select_text_from_interval(
        self, interval: Tuple[int, int], path: Optional[str] = None
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

        if not path:
            path = self.uri
        section_text = self.section_text(path)
        if len(section_text) < max(interval):
            raise ValueError(
                f"Interval {interval} extends beyond the end of text section {path}."
            )
        return section_text[min(interval) : max(interval)]

    def select_text(self, selector: TextQuoteSelector) -> Optional[str]:
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
        text = self.section_text(path=selector.path)
        if not selector.exact:
            return text
        if re.search(selector.passage_regex, text, re.IGNORECASE):
            return selector.exact
        raise ValueError(
            f'Passage "{selector.exact}" from TextQuoteSelector '
            + f'not found in Code "{self.title}" at path "{selector.path}".'
        )

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.filepath)})"

    def __str__(self):
        return self.title


@dataclass(frozen=True)
class Enactment:
    """
    A passage of legislative text.

    May be used as support for a
    :class:`.Rule`. To retrieve the text, there needs
    to be an available method for identifying the correct XML
    element based on the section and subsection names, and each
    XML format used for any :class:`Code` will require a different method.

    :param selector:
        identifier for the place in the :class:`Code` where
        the text can be found.

    :param code:
        the :class:`Code` where this legislative text appears.

    :param regime:
        a :class:`.Regime` with a :class:`.Jurisdiction` that has enacted
        the :class:`Code` where this legislative text appears.

    :param name:
        an identifier for this object, often used if the object needs
        to be referred to multiple times in the process of composing
        other :class:`.Factor` objects.
    """

    selector: TextQuoteSelector
    code: Optional[Code] = None
    regime: Optional[Regime] = None
    name: Optional[str] = None

    def __post_init__(self):
        if not self.code:
            if self.regime:
                object.__setattr__(
                    self, "code", self.regime.get_code(self.selector.path)
                )
            else:
                raise ValueError("'code' and 'regime' cannot both be None")
        if (self.selector.prefix or self.selector.suffix) and not self.selector.exact:
            object.__setattr__(
                self.selector, "exact", self.selector.set_exact_from_source(self.code)
            )
        object.__delattr__(self, "regime")

    def __add__(self, other):
        if other.__class__.__name__ == "Rule":
            return other + self
        if not isinstance(other, self.__class__):
            raise TypeError

        if self >= other and self.selector.path.startswith(other.selector.path):
            return self
        if other >= self and other.selector.path.startswith(self.selector.path):
            return other
        combined = self.combine_text(other) or other.combine_text(self)
        return combined

    def combine_text(self, other: Enactment) -> Optional[Enactment]:
        r"""
        Create new :class:`Enactment` with combined text of the source :class:`Enactment`\s.

        :param other:
            another :class:`Enactment` with text to combine with the text from ``self``.

        :returns:
            new :class:`Enactment` with combined text of the source :class:`Enactment`\s, or
            ``None`` if the :class:`Enactment`\s can't be combined.
        """
        if not other.selector.path.startswith(self.selector.path):
            return None
        self_interval = self.text_interval()
        other_interval = other.text_interval(path=self.selector.path)
        both_intervals = sorted([self_interval, other_interval])
        if both_intervals[1][0] >= both_intervals[0][1] + 2:
            return None
        new_interval = (
            both_intervals[0][0],
            max(both_intervals[0][1], both_intervals[1][1]),
        )
        # BUG: can't create prefix and suffix to distinguish identical passages.
        return Enactment(
            selector=TextQuoteSelector(
                path=self.selector.path,
                exact=self.code.select_text_from_interval(
                    interval=new_interval, path=self.selector.path
                ),
            ),
            code=self.code,
        )

    def text_interval(self, path=None) -> Optional[Tuple[int, int]]:
        """
        Find integer indices for the quoted text.

        :returns:
            A :class:`tuple` containing the lower and upper bounds of the
            text passage quoted in ``self.selector.exact`` within the
            XML section referenced in ``self.selector.path``.
        """
        if not path:
            path = self.selector.path
        regex = self.selector.passage_regex
        match = re.search(regex, self.code.section_text(path), re.IGNORECASE)
        if match:
            # Getting indices from match group 1 (in the parentheses),
            # not match 0 which includes prefix and suffix
            return (match.start(1), match.end(1))
        return None

    @property
    def effective_date(self):
        r"""
        Give effective date for the :class:`Enactment`\.

        :returns:
            the effective date of the text in this passage.
            Currently works only for the US Constitution.
        """
        return self.code.provision_effective_date(self.selector)

    @property
    def text(self):
        r"""
        Get a passage from ``self``\'s :class:`.Code` with ``self``\'s :class:`.TextQuoteSelector`.

        :returns: the full text of the cited passage from the XML.
        """

        return self.code.select_text(self.selector)

    def means(self, other: Enactment) -> bool:
        r"""
        Find whether meaning of ``self`` is equivalent to that of ``other``.

        ``Self`` must be neither broader nor narrower than ``other``, which
        means it must contain the same legislative text in the same :class:`.Code`
        from the same :class:`.Jurisdiction`

        .. note::
            You could always make the result ``False`` by comparing longer
            passages of text until you found a difference between the two
            sites in the text. Does this undercut the usefulness of the
            ``means`` method?

        :returns:
            whether ``self`` and ``other`` represent the same text
            issued by the same sovereign in the same level of
            :class:`Enactment`\.
        """
        if not isinstance(other, self.__class__):
            return False

        return (
            self.text.strip(",:;. ") == other.text.strip(",:;. ")
            and self.code.jurisdiction == other.code.jurisdiction
            and self.code.level == other.code.level
        )

    def __str__(self):
        return f'"{self.text}" ({self.code.title}, {self.selector.path})'

    def __ge__(self, other):
        """
        Tells whether ``self`` implies ``other``.

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

    def __gt__(self, other) -> bool:
        """Test whether ``self`` implies ``other`` without having same meaning."""
        if self == other:
            return False
        return self >= other


def consolidate_enactments(enactments: List[Enactment]) -> List[Enactment]:
    r"""
    Consolidate any overlapping :class:`Enactment`\s in a :class:`list`.

    :param enactments:
        a list of :class:`Enactment`\s that may include overlapping
        legislative text within the same section

    :returns:
        a list of :class:`Enactment`\s without overlapping text
    """
    consolidated: List[Enactment] = []
    while enactments:
        match_made = False
        left = enactments.pop()
        for right in enactments:
            if left + right is not None:
                enactments.remove(right)
                enactments.append(left + right)
                match_made = True
                break
        if match_made is False:
            consolidated.append(left)
    return consolidated
