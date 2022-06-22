"""Create models of assertions accepted as factual by courts."""
from __future__ import annotations
from copy import deepcopy
import operator
from typing import Any, ClassVar, Dict, Iterator, List
from typing import Mapping, Optional, Sequence, Tuple, Union

from pydantic import BaseModel, Extra, ValidationError, validator, root_validator
from slugify import slugify

from nettlesome.entities import Entity
from nettlesome.factors import Factor
from nettlesome.formatting import indented, wrapped
from nettlesome.terms import (
    Comparable,
    ContextRegister,
    Explanation,
    Term,
    TermSequence,
    new_context_helper,
)
from nettlesome.predicates import Predicate
from nettlesome.quantities import Comparison, QuantityRange


RawPredicate = Dict[str, Union[str, bool]]
RawFactor = Dict[str, Union[RawPredicate, Sequence[Any], str, bool]]


class Fact(Factor, BaseModel):
    r"""
    An assertion accepted as factual by a court.

    Often based on factfinding by a judge or jury.

    Facts may be "alleged" by a pleading, "supported" by evidence, or
    "found" to be factual by a jury verdict or a judge's finding of fact.

    :param predicate:
        a natural-language clause with zero or more slots
        to insert ``terms`` that are typically the
        subject and objects of the clause.

    :param terms:
        a series of :class:`Factor` objects that fill in
        the blank spaces in the ``predicate`` statement.

    :param name:
        an identifier for this object, often used if the object needs
        to be referred to multiple times in the process of composing
        other :class:`Factor` objects.

    :param standard_of_proof:
        a descriptor for the degree of certainty associated
        with the assertion in the ``predicate``.

    :param absent:
        whether the absence, rather than the presence, of the legal
        fact described above is being asserted.

    :param generic:
        whether this object could be replaced by another generic
        object of the same class without changing the truth of the
        :class:`Rule` in which it is mentioned.

    :attr standards_of_proof:
        a tuple with every allowable name for a standard of
        proof, in order from weakest to strongest.

        .. note:
            If any courts anywhere in a legal regime disagree about the
            relative strength of the various standards of proof, or if
            any court considers the order context-specific, then this
            approach of hard-coding their names and order will have to change.
    """

    predicate: Union[Predicate, Comparison]
    terms: List[
        Union[Entity, "Fact", "Allegation", "Pleading", "Exhibit", "Evidence"]
    ] = []
    name: str = ""
    absent: bool = False
    generic: bool = False
    standard_of_proof: Optional[str] = None
    standards_of_proof: ClassVar[Tuple[str, ...]] = (
        "scintilla of evidence",
        "substantial evidence",
        "preponderance of evidence",
        "clear and convincing",
        "beyond reasonable doubt",
    )

    class Config:
        """Fail validation if the input data has data not specified in the model."""

        extra = Extra.forbid

    @root_validator(pre=True)
    def nest_predicate_fields(cls, values):
        """Move fields passed to the Fact model that really belong to the Predicate model."""
        type_str = values.pop("type", "")
        if type_str and type_str.lower() != "fact":
            raise ValidationError(f"type {type_str} was passed to Fact model")

        if isinstance(values.get("predicate"), str):
            values["predicate"] = Predicate(content=values["predicate"])
            if "truth" in values:
                values["predicate"].truth = values.pop("truth")

        for field_name in ["content", "truth", "sign", "expression"]:
            if field_name in values:
                values["predicate"] = values.get("predicate", {})
                values["predicate"][field_name] = values.pop(field_name)
        if isinstance(values.get("predicate"), dict) and values["predicate"].get(
            "content"
        ):
            for sign in {
                **QuantityRange.opposite_comparisons,
                **QuantityRange.normalized_comparisons,
            }:
                if sign in values["predicate"]["content"]:
                    content, quantity_text = values["predicate"]["content"].split(sign)
                    values["predicate"]["content"] = content.strip()
                    values["predicate"]["expression"] = quantity_text.strip()
                    values["predicate"]["sign"] = sign
                    break
        return values

    @validator("terms", pre=True)
    def terms_as_sequence(cls, v, values) -> Sequence[Any]:
        """Convert "terms" field to a sequence."""
        if isinstance(v, Mapping):
            v = values["predicate"].template.get_term_sequence_from_mapping(v)
        if not v:
            v = []
        elif isinstance(v, Term):
            v = [v]
        return v

    @property
    def term_sequence(self) -> TermSequence:
        """Return a TermSequence of the terms in this Statement."""
        return TermSequence(self.terms)

    @property
    def terms_without_nulls(self) -> Sequence[Term]:
        """Get Terms that are not None."""
        return [term for term in self.terms if term is not None]

    @property
    def slug(self) -> str:
        """
        Get a representation of self without whitespace.

        Intended for use as a sympy :class:`~sympy.core.symbol.Symbol`
        """
        terms = [term for term in self.terms if term is not None]
        subject = self.predicate._content_with_terms(terms).removesuffix(" was")
        return slugify(subject)

    @property
    def str_with_concrete_context(self) -> str:
        """
        Identify self more verbosely, specifying which text is a concrete context factor.

        :returns:
            the same as the __str__ method, but with an added "SPECIFIC CONTEXT" section
        """
        text = str(self)
        concrete_context = [
            factor for factor in self.terms_without_nulls if not factor.generic
        ]
        if any(concrete_context) and not self.generic:
            text += "\n" + indented("SPECIFIC CONTEXT:")
            for factor in concrete_context:
                factor_text = indented(factor.wrapped_string, tabs=2)
                text += f"\n{factor_text}"
        return text

    @property
    def truth(self) -> Optional[bool]:
        """Access :attr:`~Predicate.truth` attribute."""
        return self.predicate.truth

    @validator("terms")
    def _validate_terms(cls, v, values, **kwargs):
        """Normalize ``terms`` to initialize Statement."""

        # make TermSequence for validation, then ignore it
        TermSequence.validate_terms(v)

        if values.get("predicate") is None:
            raise ValidationError("Predicate field is required.")

        if len(v) != len(values["predicate"]):
            message = (
                "The number of items in 'terms' must be "
                + f"{len(values['predicate'])}, not {len(v)}, "
                + f"to match predicate.context_slots for '{values['predicate']}'"
            )
            raise ValueError(message)
        return v

    @property
    def wrapped_string(self):
        """Wrap text in string representation of ``self``."""
        content = str(self.predicate._content_with_terms(self.terms))
        unwrapped = self.predicate._add_truth_to_content(content)
        text = wrapped(super().__str__().format(unwrapped))
        if self.standard_of_proof:
            text += "\n" + indented(f"by the STANDARD {self.standard_of_proof}")
        return text

    @validator("standard_of_proof")
    def validate_standard_of_proof(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate that standard of proof is one of the allowable values.

        :param v:
            the value to validate.

        :returns:
            the validated value.
        """
        if v is None:
            return v
        if v not in cls.standards_of_proof:
            raise ValueError(
                f"standard of proof must be one of {cls.standards_of_proof} or None."
            )
        return v

    def __str__(self):
        """Create one-line string representation for inclusion in other Facts."""
        unwrapped = self.predicate._add_truth_to_content(self.content)
        standard = (
            f"by the standard {self.standard_of_proof}, "
            if self.standard_of_proof
            else ""
        )
        string = f"{standard}{unwrapped}"
        return Comparable.__str__(self).format(string).replace(",,", ",")

    @property
    def content(self) -> str:
        """Return the content of self's Predicate."""
        return str(self.predicate._content_with_terms(self.terms))

    def _means_if_concrete(
        self, other: Comparable, context: Explanation
    ) -> Iterator[Explanation]:
        if self.standard_of_proof == other.__dict__.get(
            "standard_of_proof"
        ) and self.predicate.means(other.predicate):
            yield from super()._means_if_concrete(other, context)

    def __len__(self):
        return len(self.generic_terms())

    def _implies_if_concrete(
        self, other: Comparable, context: ContextRegister
    ) -> Iterator[ContextRegister]:
        """
        Test if ``self`` implies ``other``, assuming they are not ``generic``.

        :returns:
            whether ``self`` implies ``other`` under the given assumption.
        """
        if (
            isinstance(other, self.__class__)
            and self.predicate >= other.predicate
            and bool(self.standard_of_proof) == bool(other.standard_of_proof)
            and not (
                self.standard_of_proof
                and (
                    self.standards_of_proof.index(self.standard_of_proof)
                    < self.standards_of_proof.index(other.standard_of_proof)
                )
            )
        ):
            yield from super()._implies_if_concrete(other, context)

    def _contradicts_if_present(
        self, other: Comparable, explanation: Explanation
    ) -> Iterator[Explanation]:
        """
        Test if ``self`` contradicts :class:`Fact` ``other`` if neither is ``absent``.

        :returns:
            whether ``self`` and ``other`` can't both be true at
            the same time under the given assumption.
        """
        if isinstance(other, self.__class__) and self.predicate.contradicts(
            other.predicate
        ):
            for context in self._context_registers(
                other, operator.ge, explanation.context
            ):
                yield explanation.with_context(context)

    def negated(self) -> Fact:
        """Return copy of self with opposite truth value."""
        result = deepcopy(self)
        result.predicate = result.predicate.negated()
        return result

    @new_context_helper
    def new_context(self, changes: Dict[Comparable, Comparable]) -> Comparable:
        """
        Create new :class:`Factor`, replacing keys of ``changes`` with values.

        :returns:
            a version of ``self`` with the new context.
        """
        result = deepcopy(self)
        new_terms = TermSequence(
            [factor.new_context(changes) for factor in self.terms_without_nulls]
        )
        result.terms = list(new_terms)
        return result

    def _registers_for_interchangeable_context(
        self, matches: ContextRegister
    ) -> Iterator[ContextRegister]:
        r"""
        Find possible combination of interchangeable :attr:`terms`.

        :param matches:
            matching Terms between self and other
        :yields:
            context registers with every possible combination of
            ``self``\'s and ``other``\'s interchangeable
            :attr:`terms`.
        """
        yield matches
        gen = self.term_permutations()
        _ = next(gen)  # unchanged permutation
        already_returned: List[ContextRegister] = [matches]

        for term_permutation in gen:
            left = [term for term in self.terms if term is not None]
            right = [term for term in term_permutation if term is not None]
            changes = ContextRegister.from_lists(left, right)
            changed_registry = matches.replace_keys(changes)
            if all(
                changed_registry != returned_dict for returned_dict in already_returned
            ):
                already_returned.append(changed_registry)
                yield changed_registry

    def term_permutations(self) -> Iterator[TermSequence]:
        """Generate permutations of context factors that preserve same meaning."""
        for pattern in self.predicate.term_index_permutations():
            sorted_terms = [x for _, x in sorted(zip(pattern, self.terms))]
            yield TermSequence(sorted_terms)


def build_fact(
    predicate: Predicate,
    indices: Optional[Union[int, Sequence[int]]] = None,
    case_factors: Optional[Union[Factor, Sequence[Factor]]] = None,
    name: Optional[str] = None,
    standard_of_proof: Optional[str] = None,
    absent: bool = False,
    generic: bool = False,
):
    r"""
    Build a :class:`.Fact` with generics selected from a list.

    :param predicate:
        a natural-language clause with zero or more slots
        to insert ``terms`` that are typically the
        subject and objects of the clause.

    :param terms:
        a series of integer indices of generic factors to
        fill in the blanks in the :class:`.Predicate`

    :param name:
        an identifier for this object, often used if the object needs
        to be referred to multiple times in the process of composing
        other :class:`.Factor` objects

    :param standard_of_proof:
        a descriptor for the degree of certainty associated
        with the assertion in the :class:`.Predicate`

    :param absent:
        whether the absence, rather than the presence, of the legal
        fact described above is being asserted.

    :param generic:
        whether this object could be replaced by another generic
        object of the same class without changing the truth of the
        :class:`Rule` in which it is mentioned.

    :param case_factors:
        a series of :class:`.Factor`\s that have already been mentioned
        in the :class:`.Opinion`. They are available for composing the
        new :class:`.Factor` object and don't need to be recreated.
    """
    if not indices:
        indices = range(len(predicate))
    if isinstance(indices, int):
        indices = (indices,)

    case_factors = case_factors or ()
    if isinstance(case_factors, BaseModel):
        wrapped_factors = [case_factors]
    else:
        wrapped_factors = list(case_factors)

    terms = [wrapped_factors[i] for i in indices]
    return Fact(
        predicate=predicate,
        terms=terms,
        name=name or "",
        standard_of_proof=standard_of_proof,
        absent=absent,
        generic=generic,
    )


class Exhibit(Factor, BaseModel):
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

    offered_by: Entity
    form: Optional[str] = None
    statement: Optional[Fact] = None
    statement_attribution: Optional[Entity] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar[Tuple[str, ...]] = (
        "statement",
        "statement_attribution",
    )

    def _means_if_concrete(
        self, other: Factor, context: ContextRegister
    ) -> Iterator[ContextRegister]:
        if (
            isinstance(other, self.__class__)
            and self.form == other.form
            and self.offered_by.means(other.offered_by)
        ):
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
        string = f'{("attributed to " + self.statement_attribution.short_string) if self.statement_attribution else ""}'
        if self.statement:
            string += ", asserting " + self.statement.short_string + ","
        string = super().__str__().format(string)
        return string.replace("exhibit", self.form or "exhibit").strip()

    @property
    def wrapped_string(self):
        """Create a string describing the Exhibit split over multiple lines."""
        text = ""
        if self.form:
            text += f"in the FORM {self.form}"
        if self.statement:
            text += "\n" + indented("WITH THE ASSERTION:")
            factor_text = indented(self.statement.wrapped_string, tabs=2)
            text += f"\n{factor_text},"
        if self.statement_attribution:
            text += "\n" + indented(
                f"ATTRIBUTED TO {self.statement_attribution.wrapped_string}"
            )

        return super().__str__().format(text)


class Evidence(Factor, BaseModel):
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
    context_factor_names: ClassVar[Tuple[str, ...]] = ("exhibit", "to_effect")

    class Config:
        """Fail validation if the input data has data not specified in the model."""

        extra = Extra.forbid

    @root_validator(pre=True)
    def check_type_field(cls, values):
        """Fail valitation if the input has a "type" field without the class name."""
        type_str = values.pop("type", "")
        if type_str and type_str.lower() != "evidence":
            raise ValidationError(f"type {type_str} was passed to Evidence model")
        return values

    def __str__(self):
        string = (
            f'{("of " + self.exhibit.short_string + " ") if self.exhibit else ""}'
            + f'{("which supports " + self.to_effect.short_string) if self.to_effect else ""}'
        )
        return super().__str__().format(string).strip().replace("Evidence", "evidence")

    @property
    def wrapped_string(self):
        """Create a string describing the Evidence split over multiple lines."""
        text = ""
        if self.exhibit:
            text += "\n" + indented("OF:")
            factor_text = indented(self.exhibit.wrapped_string, tabs=2)
            text += f"\n{str(factor_text)}"
        if self.to_effect:
            text += "\n" + indented("INDICATING:")
            factor_text = indented(self.to_effect.wrapped_string, tabs=2)
            text += f"\n{factor_text}"
        return super().__str__().format(text).strip()


class Pleading(Factor, BaseModel):
    r"""
    A document filed by a party to make :class:`Allegation`\s.

    :param filer:
        the :class:`.Entity` that the pleading references as having filed it,
        regardless of any questions about the identification of the filer.

    :param name:

    :param absent:

    :param generic:
    """

    filer: Entity
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar[Tuple[str]] = ("filer",)

    def __str__(self):
        string = f'{("filed by " + self.filer.short_string if self.filer else "")}'
        return super().__str__().format(string)


class Allegation(Factor, BaseModel):
    """
    A formal assertion of a :class:`Fact`.

    May be included by a party in a :class:`Pleading`
    to establish a cause of action.

    :param statement:
        a :class:`Fact` being alleged

    :param pleading:
        the :class:`Pleading` in where the allegation appears

    :param name:

    :param absent:

    :param generic:
    """

    fact: Fact
    pleading: Optional[Pleading] = None
    name: Optional[str] = None
    absent: bool = False
    generic: bool = False
    context_factor_names: ClassVar[Tuple[str, ...]] = ("fact", "pleading")

    @property
    def wrapped_string(self):
        """Create a string describing the Allegation split over multiple lines."""
        text = ""
        if self.fact:
            text += "\n" + indented("OF:")
            factor_text = indented(self.fact.wrapped_string, tabs=2)
            text += f"\n{str(factor_text)}"
        if self.pleading:
            text += "\n" + indented("FOUND IN:")
            factor_text = indented(str(self.pleading), tabs=2)
            text += f"\n{factor_text}"
        return super().__str__().format(text).strip()

    def __str__(self):
        string = (
            f'{("in " + self.pleading.short_string + ",") if self.pleading else ""}'
            + f'{("claiming " + self.fact.short_string + ",") if self.fact else ""}'
        )
        string = string.strip(",")
        return super().__str__().format(string).replace("Allegation", "allegation")


Fact.update_forward_refs()
Exhibit.update_forward_refs()
Evidence.update_forward_refs()
Allegation.update_forward_refs()
Pleading.update_forward_refs()
