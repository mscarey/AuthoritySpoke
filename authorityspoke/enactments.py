"""Classes representing legislation."""

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
    A code of legislation.

    Could be a constitution, code of statutes, code of regulations,
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
        """Set ``filename`` parameter as attribute."""
        self.filename = filename

    @property
    def path(self):
        """
        Construct the path to this file in the ``example_data`` folder.

        :returns:
            The path to the file where the XML file for
            the code can be found.
        """
        return self.__class__.directory / self.filename

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
        with open(self.path) as fp:
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

    def select_text(self, selector: TextQuoteSelector) -> Optional[str]:
        """
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
            section = self.xml.find(identifier=selector.path)
            return section.find_all(["chapeau", "paragraph", "content"])

        if selector.path is not None:
            docpath = selector.path.replace(self.uri, "")

        if selector.path is None:  # selecting the whole Code
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
                passages = self.xml.find(id=docpath.split("/")[1]).find_all(name="text")

        elif self.jurisdiction == "us-ca":
            this_cal_section = functools.partial(cal_href, docpath)
            passages = self.xml.find(href=this_cal_section).parent.find_next_siblings(
                style="margin:0;display:inline;"
            )

        text = " ".join(" ".join(passage.text.split()) for passage in passages)
        if not selector.exact:
            return text
        prefix = selector.prefix or ""
        suffix = selector.suffix or ""
        passage_regex = (
            re.escape(prefix)
            + r"\s*"
            + re.escape(selector.exact)
            + r"\s*"
            + re.escape(suffix)
        )
        if re.search(passage_regex, text, re.IGNORECASE):
            return selector.exact
        raise ValueError(
            f"Passage {selector.exact} from TextQuoteSelector "
            + f"not found in Code at path {selector.path}."
        )

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.filename}")'

    def __str__(self):
        return self.title


@dataclass(frozen=True)
class Enactment:
    """
    A passage of legislative text.

    May be used as support for a
    :class:`.ProceduralRule`. To retrieve the text, there needs
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
    regime: Optional["Regime"] = None
    name: Optional[str] = None

    def __post_init__(self):
        if not self.code:
            if self.regime:
                object.__setattr__(
                    self, "code", self.regime.get_code(self.selector.path)
                )
            else:
                raise ValueError("'code' and 'regime' cannot both be None")
        if not self.selector.exact:
            self.selector.set_exact_from_source(self.code)
        object.__delattr__(self, "regime")

    @property
    def effective_date(self):
        """
        Give effective date for the :class:`Enactment`\.

        :returns:
            the effective date of the text in this passage.
            Currently works only for the US Constitution.
        """
        return self.code.provision_effective_date(self.selector)

    @property
    def text(self):
        """
        Get a passage from ``self``\'s :class:`.Code` with ``self``\'s :class:`.TextQuoteSelector`.

        :returns: the full text of the cited passage from the XML.
        """

        return self.code.select_text(self.selector)

    @classmethod
    @log_mentioned_context
    def from_dict(
        cls,
        enactment_dict: Dict[str, str],
        code: Optional[Code] = None,
        regime: Optional[Regime] = None,
        *args,
        **kwargs,
    ) -> Enactment:
        """
        Create a new :class:`Enactment` object using imported JSON data.

        The new :class:`Enactment` can be composed from a :class:`.Code`
        referenced in the ``regime`` parameter.

        :param enactment_dict:

        :param code:
            the :class:`.Code` that is the source for this
            :class:`Enactment`

        :param regime:
            the :class:`.Regime` where the :class:`.Code` that is the
            source for this :class:`Enactment` can be found, or where
            it should be added

        :returns:
            a new :class:`Enactment` object.
        """
        if regime and not code:
            code = regime.get_code(enactment_dict.get("path"))
        if code is None and enactment_dict.get("code"):
            code = Code(enactment_dict.get("code"))
        if code is None:
            raise ValueError(
                "Must either specify a Regime and a path to find the "
                + "Code within the Regime, or specify a filename for an XML "
                + "file that can be used to build the Code"
            )
        if regime:
            regime.set_code(code)

        selector = TextQuoteSelector(
            path=enactment_dict.get("path"),
            exact=enactment_dict.get("exact"),
            prefix=enactment_dict.get("prefix"),
            suffix=enactment_dict.get("suffix"),
            source=code,
        )

        return Enactment(code=code, selector=selector, name=enactment_dict.get("name"))

    def means(self, other: Enactment) -> bool:
        """
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
