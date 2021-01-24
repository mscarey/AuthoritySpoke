r""":class:`.Factor`\s used to support :class:`.Fact` findings."""
from dataclasses import dataclass, field

from typing import ClassVar, Iterator, List, Optional, Tuple

from anchorpoint import TextQuoteSelector

from authorityspoke.entities import Entity
from authorityspoke.factors import ContextRegister, Factor
from authorityspoke.facts import Fact
from authorityspoke.formatting import indented, wrapped


@dataclass()
class Exhibit(Factor):
    """
    A source of information for use in litigation.

    :param form:
        a term describing the category of exhibit. For example: testimony,
        declaration, document, or recording.

    :param statement:
        a fact assertion made via the exhibit. For instance, if the exhibit
        is a document, this parameter could refer to a statement printed
        on the document.

    :param statement_attribution:
        the :class:`.Entity` that the exhibit imputes the statement to. For
        instance, for a signed declaration, this would refer to the person
        whose signature appears on the declaration, regardless of any
        authentication concerns. The statement_attribution parameter may
        appear without the statement parameter, especially if the content
        of the statement is irrelevant.

    :param name:
        a string identifier for the exhibit

    :param absent:
        if True, indicates that no exhibit meeting the description exists
        in the litigation. If the exhibit has merely been rejected as
        evidence, use the absent attribute on an :class:`Evidence` object
        instead.

    :param generic:
        if True, indicates that the specific attributes of the exhibit
        are irrelevant in the context of the :class:`.Holding` where
        the exhibit is being referenced.

    .. note
        The form parameter may be replaced by a limited
        ontology of terms when sufficient example data is available.
    """

    form: Optional[str] = None
    statement: Optional[Fact] = None
    statement_attribution: Optional[Entity] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    anchors: List[TextQuoteSelector] = field(default_factory=list)
    context_factor_names: ClassVar[Tuple[str, ...]] = (
        "statement",
        "statement_attribution",
    )

    def _means_if_concrete(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        if isinstance(other, self.__class__) and self.form == other.form:
            yield from super()._means_if_concrete(other, context)

    def _implies_if_concrete(
        self, other: Factor, context: Optional[ContextRegister] = None
    ) -> Iterator[ContextRegister]:
        if isinstance(other, self.__class__) and (
            self.form == other.form or other.form is None
        ):
            yield from super()._implies_if_concrete(other, context)

    def __str__(self):
        """Represent object as string without line breaks."""
        string = (
            f'{("attributed to " + self.statement_attribution.short_string + ", ") if self.statement_attribution else ""}'
            + f'{("asserting " + self.statement.short_string + ", ") if self.statement else ""}'
        )
        string = super().__str__().format(string)
        return string.replace("Exhibit", self.form or "exhibit").strip()

    @property
    def wrapped_string(self):
        text = ""
        if self.form:
            text += f"in the FORM {self.form}"
        if self.statement:
            text += "\n" + indented("WITH THE ASSERTION:")
            factor_text = indented(self.statement.wrapped_string, tabs=2)
            text += f"\n{str(factor_text)},"
        if self.statement_attribution:
            text += "\n" + indented(
                f"ATTRIBUTED TO {self.statement_attribution.wrapped_string}"
            )

        return super().__str__().format(text)


@dataclass()
class Evidence(Factor):
    """
    An :class:`Exhibit` admitted by a court to aid a factual determination.

    :param exhibit:
        the thing that is being used to aid a factual determination

    :param to_effect:
        the :class:`.Fact` finding that would be supported by the evidence.
        If the Fact object includes a non-null standard_of_proof attribute, it
        indicates that that the evidence would support a factual finding by
        that standard of proof.

    :param name:
        a string identifier

    :param absent:
        if True, indicates that no evidence meeting the description has been
        admitted, regardless of whether a corresponding :class:`Exhibit` has
        been presented

    :param generic:
        if True, indicates that the specific attributes of the evidence
        are irrelevant in the context of the :class:`.Holding` where
        the evidence is being referenced.
    """

    exhibit: Optional[Exhibit] = None
    to_effect: Optional[Fact] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    anchors: List[TextQuoteSelector] = field(default_factory=list)
    context_factor_names: ClassVar[Tuple[str, ...]] = ("exhibit", "to_effect")

    def __str__(self):
        string = (
            f'{("of " + self.exhibit.short_string + ", ") if self.exhibit else ""}'
            + f'{("which supports " + self.to_effect.short_string) if self.to_effect else ""}'
        )
        return super().__str__().format(string).strip().replace("Evidence", "evidence")

    @property
    def wrapped_string(self):
        text = ""
        if self.exhibit:
            text += "\n" + indented("OF:")
            factor_text = indented(self.exhibit.wrapped_string, tabs=2)
            text += f"\n{str(factor_text)}"
        if self.to_effect:
            text += "\n" + indented("INDICATING:")
            factor_text = indented(self.to_effect.wrapped_string, tabs=2)
            text += f"\n{str(factor_text)}"
        return super().__str__().format(text).strip()
