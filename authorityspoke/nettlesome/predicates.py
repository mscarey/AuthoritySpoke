r"""
Phrases that contain meanings of :class:`.Statement`\s.

Can contain references to other :class:`.Statement`\s,
to numeric values, to dates, or to quantities (with the use of
the `pint <https://pint.readthedocs.io/en/>`_ library).
"""

from __future__ import annotations
from abc import ABCMeta
import re

from itertools import product
from string import templatelib
from typing import Any, Dict, Mapping
from typing import List, Optional, Sequence, Set, Tuple

from pydantic import BaseModel

from authorityspoke.nettlesome.terms import Comparable, TermSequence
from authorityspoke.nettlesome.terms import Term


Interpolation = templatelib.Interpolation
TStringTemplate = templatelib.Template


class StatementTemplate:
    r"""
    A text template for a Predicate.

    Should include placeholders for any replaceable :class:`~nettlesome.terms.Term`\s
    that can be substituted into the :class:`~nettlesome.predicates.Predicate`\.
    """

    _PLACEHOLDER_PATTERN = re.compile(
        r"(?<!\{)\{(?P<named>[_a-zA-Z][_a-zA-Z0-9]*)\}(?!\})"
    )

    def __init__(self, template: str, make_singular: bool = True) -> None:
        r"""
        Identify placeholders in template text, and make verbs singular if needed.

            >>> school_template = StatementTemplate(
            ... "{group} were at school", make_singular=True)
            >>> str(school_template)
            'StatementTemplate("{group} was at school")'

        The make_singular flag only affects verbs immediately after :class:`~nettlesome.terms.Term`\s.

            >>> text = "{group} thought the exams were difficult"
            >>> exams_template = StatementTemplate(text, make_singular=True)
            >>> str(exams_template)
            'StatementTemplate("{group} thought the exams were difficult")'

        :param template:
            text containing `{placeholder}` markers for term substitution

        :param make_singular:
            whether "were" after a placeholder should be converted to
            singular "was"
        """
        self._placeholders: List[str] = []
        self._placeholder_tokens: List[str] = []
        self._t_template = TStringTemplate(template)
        self._refresh_parsed_template(template)

        if make_singular:
            self.make_content_singular()

    def __str__(self) -> str:
        return f'StatementTemplate("{self.template}")'

    def make_content_singular(self) -> None:
        """Convert template text for self.context to singular "was"."""
        strings = list(self._t_template.strings)
        for idx in range(1, len(strings)):
            if strings[idx].startswith(" were"):
                strings[idx] = " was" + strings[idx][5:]

        fragments: List[str | Interpolation] = [strings[0]]
        for idx, token in enumerate(self._placeholder_tokens):
            placeholder_name = token[1:-1]
            fragments.append(
                Interpolation(placeholder_name, placeholder_name, None, "")
            )
            fragments.append(strings[idx + 1])
        self._t_template = TStringTemplate(*fragments)
        return None

    def _refresh_parsed_template(self, template_text: str) -> None:
        """Parse {placeholders} into a templatelib.Template-backed representation."""
        fragments: List[str | Interpolation] = []
        placeholders_in_order: List[str] = []
        placeholder_tokens: List[str] = []
        start = 0

        for match in self._PLACEHOLDER_PATTERN.finditer(template_text):
            fragments.append(template_text[start : match.start()])
            named = match.group("named")
            if named is not None:
                placeholders_in_order.append(named)
                placeholder_tokens.append(f"{{{named}}}")
                fragments.append(Interpolation(named, named, None, ""))

            start = match.end()

        fragments.append(template_text[start:])
        self._placeholders = list(dict.fromkeys(placeholders_in_order))
        self._placeholder_tokens = placeholder_tokens
        self._t_template = TStringTemplate(*fragments)

    @property
    def template(self) -> str:
        """Text representation reconstructed from the stored t-template."""
        strings = self._t_template.strings
        rebuilt_template: List[str] = [strings[0]]
        for idx, token in enumerate(self._placeholder_tokens):
            rebuilt_template.append(token)
            rebuilt_template.append(strings[idx + 1])
        return "".join(rebuilt_template)

    def substitute(
        self, mapping: Optional[Mapping[str, Any]] = None, /, **kwargs: Any
    ) -> str:
        """Substitute placeholders in template text with values from mapping and kwargs."""
        substitutions: Dict[str, Any] = {}
        if mapping is not None:
            substitutions.update(mapping)
        substitutions.update(kwargs)

        chunks: List[str] = []
        for chunk in self._t_template:
            if isinstance(chunk, str):
                chunks.append(chunk)
                continue

            key = chunk.expression
            if key not in substitutions:
                raise KeyError(key)
            chunks.append(str(substitutions[key]))

        return "".join(chunks)

    def get_template_with_plurals(self, context: Sequence[Term]) -> str:
        """
        Get a version of self with "was" replaced by "were" for any plural terms.

        Does not modify this object's template attribute.
        """
        strings = list(self._t_template.strings)
        placeholders = self.placeholders
        self._check_number_of_terms(placeholders, context)
        for idx, factor in enumerate(context):
            if factor.__dict__.get("plural") is True and strings[idx + 1].startswith(
                " was"
            ):
                strings[idx + 1] = " were" + strings[idx + 1][4:]

        rebuilt_template: List[str] = [strings[0]]
        for idx, token in enumerate(self._placeholder_tokens):
            rebuilt_template.append(token)
            rebuilt_template.append(strings[idx + 1])
        return "".join(rebuilt_template)

    @property
    def placeholders(self) -> List[str]:
        """List substrings of template text marked as placeholders."""
        return self._placeholders

    @property
    def text_fragments(self) -> Tuple[str, ...]:
        """Literal text segments between placeholders in the parsed template."""
        return self._t_template.strings

    def get_term_sequence_from_mapping(
        self, term_mapping: Mapping[str, Term]
    ) -> TermSequence:
        """Get an ordered list of terms from a mapping of placeholder names to terms."""
        placeholders = self.placeholders
        result = [term_mapping[placeholder] for placeholder in placeholders]
        return TermSequence(root=tuple(result))

    def _check_number_of_terms(
        self, placeholders: List[str], context: Sequence[Term]
    ) -> None:
        if len(set(placeholders)) != len(context):
            raise ValueError(
                f"The number of terms passed in 'context' ({len(context)}) must be equal to the "
                f"number of placeholders in the StatementTemplate ({len(placeholders)})."
            )
        return None

    def mapping_placeholder_to_term(
        self, context: Sequence[Term]
    ) -> Dict[str, Comparable]:
        """
        Get a mapping of template placeholders to context terms.

        :param context:
            a list of context :class:`.factors.Factor`/s, in the same
            order they appear in the template string.
        """
        self._check_number_of_terms(self.placeholders, context)
        return dict(zip(self.placeholders, context))

    def mapping_placeholder_to_term_name(
        self, context: Sequence[Term]
    ) -> Dict[str, str]:
        """
        Get a mapping of template placeholders to the names of their context terms.

        :param context:
            a list of :class:`~authorityspoke.comparable.Comparable`
            context terms in the same
            order they appear in the template string.
        """
        mapping = self.mapping_placeholder_to_term(context)
        return {k: v.short_string for k, v in mapping.items()}

    def substitute_with_plurals(self, terms: Sequence[Term]) -> str:
        """
        Update template text with strings representing Comparable terms.

        :param context:
            terms with `.short_string()`
            methods to substitute into template, and optionally with `plural`
            attributes to indicate whether to change the word "was" to "were"

        :returns:
            updated version of template text
        """
        new_content = self.get_template_with_plurals(context=terms)
        substitutions = self.mapping_placeholder_to_term_name(context=terms)
        new_template = self.__class__(new_content, make_singular=False)
        return new_template.substitute(substitutions)


class PhraseABC(metaclass=ABCMeta):
    r"""Abstract base class for phrases that can be compared like Predicates."""

    content: str
    truth: Optional[bool]

    def contradicts(self, other: Any) -> bool:
        r"""
        Test whether ``other`` and ``self`` have contradictory meanings.

        This is determined only by the ``truth`` value, the exact template
        content, and whether the placeholders indicate interchangeable terms.
        """
        if not self._same_meaning_as_true_predicate(other):
            return False

        if self.truth is None or other.truth is None:
            return False

        return self.truth != other.truth

    def means(self, other: Any) -> bool:
        """
        Test if ``self`` and ``other`` have identical meanings.

        The means method will return False based on any difference in
        the Predicate's template text, other than the placeholder names.

        >>> talked = Predicate(content="{speaker} talked to {listener}")
        >>> spoke = Predicate(content="{speaker} spoke to {listener}")
        >>> talked.means(spoke)
        False

        The means method will also return False if there are differences in
        which placeholders are marked as interchangeable.

        >>> game_between_others = Predicate(
        ...     content="{organizer1} and {organizer2} planned for {player1} to play {game} against {player2}.")
        >>> game_between_each_other = Predicate(
        ...     content="{organizer1} and {organizer2} planned for {organizer1} to play {game} against {organizer2}.")
        >>> game_between_others.means(game_between_each_other)
        False

        :param other:
            an object to compare
        :returns:
            whether ``other`` is another Predicate with the same text,
            truth value, and pattern of interchangeable placeholders
        """

        if not self._same_meaning_as_true_predicate(other):
            return False

        return self.truth == other.truth

    def implies(self, other: Any) -> bool:
        """
        Test whether ``self`` implies ``other``.

        A Predicate implies another Predicate only if
        it :meth:`~nettlesome.predicates.Predicate.means` the
        other Predicate, or if the other Predicate has the same
        text but a truth value of None.

            >>> lived_at = Predicate(
            ...     content="{person} lived at {place}",
            ...     truth=True)
            >>> whether_lived_at = Predicate(
            ...     content="{person} lived at {place}",
            ...     truth=None)
            >>> str(whether_lived_at)
            'whether {person} lived at {place}'
            >>> lived_at.implies(whether_lived_at)
            True
            >>> whether_lived_at.implies(lived_at)
            False

        :param other:
            an object to compare for implication.

        :returns:
            whether ``other`` is another Predicate with the
            same text, and the same truth value or no truth value.
        """
        if self.truth is None:
            return False
        if not isinstance(other, self.__class__):
            return False
        if not self._same_meaning_as_true_predicate(other):
            return False
        if other.truth is None:
            return True
        return self.truth == other.truth

    def __gt__(self, other: Any) -> bool:
        r"""Alias for :meth:`~nettlesome.predicates.Predicate.implies`\."""
        return self.implies(other)

    def __ge__(self, other: Any) -> bool:
        r"""
        Test whether ``self`` either implies or has the same meaning as ``other``.

        :param other:
            an object to compare

        :returns:
            whether ``other`` is another Predicate that ``self`` either
            :meth:`~nettlesome.predicates.Predicate.means`
            or :meth:`~nettlesome.predicates.Predicate.implies`
        """

        if self.means(other):
            return True
        return self.implies(other)

    def __len__(self):
        r"""
        Get the number of Terms expected.

        Also called the linguistic valency, arity, or adicity.

        :returns:
            the number of :class:`~nettlesome.terms.Term`\s that can fit
            in the placeholders
            in the :class:`~nettlesome.predicates.StatementTemplate`\.
        """

        return len(set(self.template.placeholders))

    @property
    def template(self) -> StatementTemplate:
        """
        A text template for the predicate.

        :returns:
            a :class:`StatementTemplate` object
        """
        return StatementTemplate(self.content, make_singular=True)

    def _content_with_terms(self, terms: Sequence[Term]) -> str:
        r"""
        Make a sentence by filling in placeholders with names of Factors.

        :param context:
            terms to be mentioned in the context of
            this Predicate. They do not need to be type :class:`.Entity`

        :returns:
            a sentence created by substituting string representations
            of terms for the placeholders in the content template
        """
        return self.template.substitute_with_plurals(terms)

    def same_content_meaning(self, other: PhraseABC) -> bool:
        """
        Test if :attr:`~Predicate.content` strings of ``self`` and ``other`` have same meaning.

        :param other:
            another :class:`Predicate` being compared to ``self``

        :returns:
            whether ``self`` and ``other`` have :attr:`~Predicate.content` strings
            similar enough to be considered to have the same meaning.
        """
        left_fragments = tuple(
            fragment.lower() for fragment in self.template.text_fragments
        )
        right_fragments = tuple(
            fragment.lower() for fragment in other.template.text_fragments
        )
        return left_fragments == right_fragments

    def same_term_positions(self, other: PhraseABC) -> bool:
        """Test if self and other have same positions for interchangeable Terms."""

        return list(self.term_positions().values()) == list(
            other.term_positions().values()
        )

    def _same_meaning_as_true_predicate(self, other: PhraseABC) -> bool:
        """Test if self and other mean the same if they are both True."""
        if not isinstance(other, PhraseABC):
            raise TypeError(
                f"Type {self.__class__.__name__} can't imply, contradict, or "
                f"have same meaning as type {other.__class__.__name__}"
            )

        if not isinstance(other, self.__class__):
            return False

        if not self.same_content_meaning(other):
            return False

        return self.same_term_positions(other)

    def term_positions(self) -> Dict[str, Set[int]]:
        """
        Create list of positions that each term could take without changing Predicate's meaning.

        Assumes that if placeholders are the same except for a final digit, that means
        they've been labeled as interchangeable with one another.
        """

        without_duplicates: List[str] = self.template.placeholders
        result: Dict[str, Set[int]] = {p: {i} for i, p in enumerate(without_duplicates)}

        for index, placeholder in enumerate(without_duplicates):
            if placeholder[-1].isdigit:
                for k, v in result.items():
                    if k[-1].isdigit() and k[:-1] == placeholder[:-1]:
                        result[k].add(index)
        return result

    def term_index_permutations(self) -> List[Tuple[int, ...]]:
        """Get the arrangements of all this Predicate's terms that preserve the same meaning."""
        product_of_positions = product(*self.term_positions().values())
        return [x for x in product_of_positions if len(set(x)) == len(x)]

    def _add_truth_to_content(self, content: str) -> str:
        """Get self's content with a prefix indicating the truth value."""
        if self.truth is None:
            truth_prefix = "whether "
        elif self.truth is False:
            truth_prefix = "it was false that "
        else:
            truth_prefix = "that "
        return f"{truth_prefix}{content}"


class Predicate(PhraseABC, BaseModel, extra="forbid"):
    r"""
    A statement about real events or about a legal conclusion.

    Should contain an English-language phrase in the past tense. The past tense
    is used because legal analysis is usually backward-looking,
    determining the legal effect of past acts or past conditions.

    Don't use capitalization or end punctuation to signal the beginning
    or end of the phrase, because the phrase may be used in a
    context where it's only part of a longer sentence.

    If you need to mention the same term more than once in a Predicate,
    use the same placeholder for that term each time. If you later create
    a Fact object using the same Predicate, you will only include each unique
    term once.

        >>> # the template has two placeholders referring to the identical term
        >>> opened = Predicate(content="{applicant} opened a bank account for {applicant} and {cosigner}")

    Sometimes, a Predicate or Comparison needs to mention two terms that are
    different from each other, but that have interchangeable positions in that
    particular phrase. To convey interchangeability, the template string should
    use identical text for the placeholders for the interchangeable terms,
    except that the different placeholders should each end with a different digit.

        >>> # the template has two placeholders referring to different but interchangeable terms
        >>> members = Predicate(content="{relative1} and {relative2} both were members of the same family")

    :param template:
        a clause containing an assertion in English in the past tense, with
        placeholders showing where references to specific terms
        from the case can be inserted to make the clause specific.
        This string must be a valid Python :py:class:`string.Template`\.

    :param truth:
        indicates whether the clause in ``content`` is asserted to be
        true or false. ``None`` indicates an assertion as to "whether"
        the clause is true or false, without specifying which.

    """

    content: str
    truth: Optional[bool] = True

    def negated(self) -> Predicate:
        """Copy ``self``, with the opposite truth value."""
        return Predicate(
            content=self.content,
            truth=not self.truth,
        )

    def __str__(self):
        return self._add_truth_to_content(self.content)
