r"""
Phrases that contain meanings of :class:`.Factor`\s, particularly :class:`.Fact`\s.

Can contain references to other :class:`.Factor`\s,
to numeric values, or to quantities (with the use of
the `pint <https://pint.readthedocs.io/en/0.9/>`_ library.)
"""

from __future__ import annotations

from itertools import product
import re

from string import Template
from typing import Any, ClassVar, Dict, Iterable, Iterator
from typing import List, Optional, Sequence, Set, Union

from pint import UnitRegistry

from authorityspoke.factors import Factor

ureg = UnitRegistry()
Q_ = ureg.Quantity


class StatementTemplate(Template):
    def __init__(self, template: str, make_singular: bool = True) -> None:
        super().__init__(template)
        if make_singular:
            self.make_content_singular()

    def __str__(self) -> str:
        return f"StatementTemplate({self.template})"

    def make_content_singular(self) -> None:
        """Convert template text for self.context to singular "was"."""
        for placeholder in self.get_placeholders():
            named_pattern = "$" + placeholder + " were"
            braced_pattern = "${" + placeholder + "} were"
            self.template = self.template.replace(
                named_pattern, "$" + placeholder + " was"
            )
            self.template = self.template.replace(
                braced_pattern, "$" + placeholder + " was"
            )
        return None

    def get_template_with_plurals(self, context: Sequence[Factor]) -> str:
        """
        Get a version of self with "was" replaced by "were" for any plural terms.

        Does not modify this object's template attribute.
        """
        result = self.template[:]
        placeholders = self.get_placeholders()
        self._check_number_of_terms(placeholders, context)
        for idx, factor in enumerate(context):
            if factor.__dict__.get("plural") is True:
                named_pattern = "$" + placeholders[idx] + " was"
                braced_pattern = "${" + placeholders[idx] + "} was"
                result = result.replace(
                    named_pattern, "$" + placeholders[idx] + " were"
                )
                result = result.replace(
                    braced_pattern, "$" + placeholders[idx] + " were"
                )
        return result

    def get_placeholders(self) -> List[str]:
        r"""
        Count bracket pairs in ``self.template``.

        :returns:
            the number of context :class:`.Factor`\s that must be
            specified to fill in the blanks in ``self.template``.
        """

        placeholders = [
            m.group("named") or m.group("braced")
            for m in self.pattern.finditer(self.template)
            if m.group("named") or m.group("braced")
        ]
        return list(dict.fromkeys(placeholders))

    def _check_number_of_terms(
        self, placeholders: List[str], context: Sequence[Factor]
    ) -> None:
        if len(set(placeholders)) != len(context):
            raise ValueError(
                f"The number of terms passed in 'context' ({len(context)}) must be equal to the "
                f"number of placeholders in the StatementTemplate ({len(placeholders)})."
            )
        return None

    def mapping_placeholder_to_term(
        self, context: Sequence[Factor]
    ) -> Dict[str, Factor]:
        """
        Get a mapping of template placeholders to context terms.

        :param context:
            a list of context :class:`.factors.Factor`/s, in the same
            order they appear in the template string.
        """
        placeholders = self.get_placeholders()
        self._check_number_of_terms(placeholders, context)
        return dict(zip(placeholders, context))

    def mapping_placeholder_to_term_name(
        self, context: Sequence[Factor]
    ) -> Dict[str, str]:
        """
        Get a mapping of template placeholders to the names of their context terms.

        :param context:
            a list of context :class:`.factors.Factor`/s, in the same
            order they appear in the template string.
        """
        mapping = self.mapping_placeholder_to_term(context)
        mapping_to_string = {k: v.short_string for k, v in mapping.items()}
        return mapping_to_string

    def substitute_with_plurals(self, context: Sequence[Factor]) -> str:
        """
        Update template text with strings representing Factor terms.

        :param context:
            Factors with :meth:`~authorityspoke.factors.Factor.short_string`
            methods to substitute into template, and optionally with `plural`
            attributes to indicate whether to change the word "was" to "were"

        :returns:
            updated version of template text
        """
        new_content = self.get_template_with_plurals(context=context)
        substitutions = self.mapping_placeholder_to_term_name(context=context)
        new_template = self.__class__(new_content, make_singular=False)
        return new_template.substitute(substitutions)


class Predicate:
    r"""
    A statement about real events or about a legal conclusion.

    Predicates may be "alleged" by a pleading, "supported" by evidence, or
    "found" to be factual by a jury verdict or a judge's finding of fact.
    The past tense is used because legal analysis is usually backward-looking,
    determining the legal effect of past acts or past conditions.

    :param template:
        a clause containing an assertion in English in the past tense, with
        placeholders showing where references to specific
        :class:`~authorityspoke.factors.Factor`\s
        from the case can be inserted to make the clause specific.
        This string must be a valid Python :py:class:`string.Template`\.
        Don't use capitalization or end punctuation to signal the beginning
        or end of the phrase, because the phrase may be used in a
        context where it's only part of a longer sentence.


    :param truth:
        indicates whether the clause in ``content`` is asserted to be
        true or false. ``None`` indicates an assertion as to "whether"
        the clause is true or false, without specifying which.

    """

    def __init__(self, template: str, truth: Optional[bool] = True, *args, **kwargs):
        """
        Clean up and test validity of attributes.

        If the :attr:`content` sentence is phrased to have a plural
        context factor, normalizes it by changing "were" to "was".
        """
        self.template = StatementTemplate(template, make_singular=True)
        self.truth = truth

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(template="{self.template.template}", '
            f"truth={self.truth}, "
        )

    @property
    def content(self) -> str:
        return self.template.template

    def content_without_placeholders(self) -> str:
        changes = {p: "{}" for p in self.template.get_placeholders()}
        return self.template.substitute(**changes)

    def content_with_terms(self, context: Union[Factor, Sequence[Factor]]) -> str:
        r"""
        Make a sentence by filling in placeholders with names of Factors.

        :param context:
            :class:`.Factor`\s to be mentioned in the context of
            this Predicate. They do not need to be type :class:`.Entity`

        :returns:
            a sentence created by substituting string representations
            Factors for the placeholders in the content template
        """

        if not isinstance(context, Iterable):
            context = (context,)
        with_plurals = self.template.substitute_with_plurals(context)

        return with_plurals

    def contradicts(self, other: Any) -> bool:
        r"""
        Test whether ``other`` and ``self`` have contradictory meanings.

        This is determined only by the ``truth`` value, the exact template
        content, and whether the placeholders indicate interchangeable terms.
        """

        if not isinstance(other, self.__class__):
            return False
        return self._contradicts_predicate(other)

    def _contradicts_predicate(self, other: Predicate) -> bool:
        if self.truth is None or other.truth is None:
            return False

        if not (self.same_content_meaning(other) and self.same_term_positions(other)):
            return False

        return self.truth != other.truth

    def same_content_meaning(self, other: Predicate) -> bool:
        """
        Test if :attr:`~Predicate.content` strings of ``self`` and ``other`` have same meaning.

        This once was used to disregard differences between "was" and "were",
        but that now happens in :meth:`Predicate.__post_init__`.

        :param other:
            another :class:`Predicate` being compared to ``self``

        :returns:
            whether ``self`` and ``other`` have :attr:`~Predicate.content` strings
            similar enough to be considered to have the same meaning.
        """
        return (
            self.content_without_placeholders().lower()
            == other.content_without_placeholders().lower()
        )

    def same_term_positions(self, other: Predicate) -> bool:

        return list(self.term_positions().values()) == list(
            other.term_positions().values()
        )

    def _same_meaning_if_true(self, other: Predicate) -> bool:
        """
        Test whether ``self`` and ``other`` mean the same if they are both True.
        """
        if not isinstance(other, self.__class__):
            return False

        if not self.same_content_meaning(other):
            return False

        return self.same_term_positions(other)

    def means(self, other: Predicate) -> bool:
        """
        Test whether ``self`` and ``other`` have identical meanings.

        To return ``True``, ``other`` can be neither broader nor narrower.
        """

        if not self._same_meaning_if_true(other):
            return False

        return self.truth == other.truth

    def __gt__(self, other: Predicate) -> bool:
        """
        Test whether ``self`` implies ``other``.

        :returns:
            whether ``self`` implies ``other``, which is ``True``
            if their statements about quantity imply it.
        """
        return self.implies(other)

    def implies(self, other: Predicate) -> bool:
        """
        Test whether ``self`` implies ``other``.
        """
        if self.truth is None:
            return False
        if not self._same_meaning_if_true(other):
            return False
        if other.truth is None:
            return True
        return self.truth == other.truth

    def __ge__(self, other: Predicate) -> bool:
        if self.means(other):
            return True
        return self.implies(other)

    def excludes_other_quantity(self, other: Predicate) -> bool:
        """Test if quantity ranges in self and other are non-overlapping."""
        if (
            not self.expression
            or not other.expression
            or not self.consistent_dimensionality(other)
        ):
            return False

        if self.expression > other.expression:
            if "<" not in self.sign and ">" not in other.sign:
                return True
        if self.expression < other.expression:
            if ">" not in self.sign and "<" not in other.sign:
                return True
        return self.expression == other.expression and (
            ("=" in self.sign) != ("=" in other.sign)
        )

    def includes_other_quantity(self, other: Predicate) -> bool:
        """Test if the range of quantities mentioned in self is a subset of other's."""
        if not self.expression or not other.expression:
            return bool(self.expression)

        if not self.consistent_dimensionality(other):
            return False

        if (
            (self.expression < other.expression)
            and ("<" in self.sign or "=" in self.sign)
            and ("<" in other.sign)
        ):
            return True
        if (
            (self.expression > other.expression)
            and (">" in self.sign or "=" in self.sign)
            and (">" in other.sign)
        ):
            return True
        if "=" in self.sign:
            if ("<" in other.sign and self.expression < other.expression) or (
                ">" in other.sign and self.expression > other.expression
            ):
                return True
        return self.expression == other.expression and (
            ("=" in self.sign) == ("=" in other.sign)
        )

    def __len__(self):
        """
        Also called the linguistic valency, arity, or adicity.

        :returns:
            the number of entities that can fit in the pairs of brackets
            in the predicate. ``self.expression`` doesn't count as one of these entities,
            even though the place where ``self.expression`` goes in represented by brackets
            in the ``self.content`` string.
        """

        return len(set(self.template.get_placeholders()))

    def negated(self) -> Predicate:
        """Copy ``self``, with the opposite truth value."""
        return Predicate(
            template=self.content,
            truth=not self.truth,
        )

    def term_positions(self):
        """
        Create list of positions that each term could take without changing Predicate's meaning.

        Assumes that if placeholders are the same except for a final digit, that means
        they've been labeled as interchangeable with one another.
        """

        without_duplicates = self.template.get_placeholders()
        result = {p: {i} for i, p in enumerate(without_duplicates)}

        for index, placeholder in enumerate(without_duplicates):
            if placeholder[-1].isdigit:
                for k in result.keys():
                    if k[-1].isdigit() and k[:-1] == placeholder[:-1]:
                        result[k].add(index)
        return result

    def term_index_permutations(self) -> List[List[int]]:
        """Get the arrangements of all this Predicate's terms that preserve the same meaning."""
        product_of_positions = product(*self.term_positions().values())
        without_duplicates = [x for x in product_of_positions if len(set(x)) == len(x)]
        return without_duplicates

    def add_truth_to_content(self, content: str) -> str:
        if self.truth is None:
            truth_prefix = "whether "
        elif self.truth is False:
            truth_prefix = "it was false that "
        else:
            truth_prefix = "that "
        return f"{truth_prefix}{content}"

    def __str__(self):
        return self.add_truth_to_content(self.content)


class Comparison(Predicate):
    r"""
    A Predicate that compares a described quantity to a constant.

    :param sign:
        A string representing an equality or inequality sign like ``==``,
        ``>``, or ``<=``. Used to indicate that the clause ends with a
        comparison to some quantity. Should be defined if and only if a
        ``quantity`` is defined. Even though "=" is the default, it's
        the least useful, because courts almost always state rules that
        are intended to apply to quantities above or below some threshold.

    :param quantity:
        a Python number object or :class:`ureg.Quantity` from the
        `pint <https://pint.readthedocs.io/en/0.9/>`_ library. Comparisons to
        quantities can be used to determine whether :class:`Predicate`\s
        imply or contradict each other. A single :class:`Predicate`
        may contain no more than one ``sign`` and one ``quantity``.
    """

    opposite_comparisons: ClassVar[Dict[str, str]] = {
        ">=": "<",
        "==": "!=",
        "<>": "=",
        "<=": ">",
        "=": "!=",
        ">": "<=",
        "<": ">=",
    }
    normalized_comparisons: ClassVar[Dict[str, str]] = {"==": "=", "!=": "<>"}

    def __init__(
        self,
        template: str,
        sign: str = "=",
        expression: Union[int, float, ureg.Quantity] = 0,
        truth: Optional[bool] = True,
    ):
        """
        Clean up and test validity of attributes.

        If the :attr:`content` sentence is phrased to have a plural
        context factor, normalizes it by changing "were" to "was".
        """
        super().__init__(template, truth=truth)
        self.sign = sign
        self.expression = self.read_quantity(expression)

        if self.sign and self.sign not in self.opposite_comparisons.keys():
            raise ValueError(
                f'"sign" string parameter must be one of {self.opposite_comparisons.keys()}.'
            )

        if self.sign and self.truth is False:
            self.truth = True
            self.sign = self.opposite_comparisons[self.sign]

        if self.expression is not None and not self.content.endswith("was"):
            raise ValueError(
                "If a Predicate includes a quantity, its 'content' must end "
                "with the word 'was' to signal the comparison with the quantity. "
                f"The word 'was' is not the end of the string '{self.content}'."
            )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(template="{self.template.template}", '
            f"truth={self.truth}, "
            f'comparison="{self.sign}", quantity={self.expression})'
        )

    @classmethod
    def read_quantity(
        cls, value: Union[float, int, str]
    ) -> Union[float, int, ureg.Quantity]:
        """
        Create pint quantity object from text.

        See `pint tutorial <https://pint.readthedocs.io/en/0.9/tutorial.html>`_

        :param quantity:
            when a string is being parsed for conversion to a
            :class:`Comparison`, this is the part of the string
            after the equals or inequality sign.
        :returns:
            a Python number object or a :class:`Quantity`
            object created with `pint.UnitRegistry
            <https://pint.readthedocs.io/en/0.9/tutorial.html>`_.
        """
        if value is None:
            return None
        if isinstance(value, (int, float, ureg.Quantity)):
            return value
        quantity = value.strip()
        if quantity.isdigit():
            return int(quantity)
        float_parts = quantity.split(".")
        if len(float_parts) == 2 and all(
            substring.isnumeric() for substring in float_parts
        ):
            return float(quantity)
        return Q_(quantity)

    def add_truth_to_content(self, content: str) -> str:
        content = super().add_truth_to_content(content)
        return f"{content} {self.expression_comparison()}"

    def consistent_dimensionality(self, other: Comparison) -> bool:
        """Test if ``other`` has a quantity parameter consistent with ``self``."""
        if not isinstance(other, Comparison):
            return False

        if isinstance(self.expression, ureg.Quantity):
            if not isinstance(other.expression, ureg.Quantity):
                return False
            if self.expression.dimensionality != other.expression.dimensionality:
                return False
        elif isinstance(other.expression, ureg.Quantity):
            return False
        return True

    def implies(self, other: Predicate) -> bool:

        if not super().implies(other):
            return False

        if not (self.expression and other.expression and self.sign and other.sign):
            return False

        return self.includes_other_quantity(other)

    def means(self, other: Predicate) -> bool:

        if not super().means(other):
            return False

        return self.expression == other.expression and self.sign == other.sign

    def contradicts(self, other: Any) -> bool:
        """
        Test whether ``other`` and ``self`` have contradictory meanings.

        If the checks in the Predicate class find no contradiction, this
        method looks for a contradiction in the dimensionality detected by the
        ``pint`` library, or in the possible ranges for each Comparison's
        numeric ``expression``.
        """
        if not isinstance(other, self.__class__):
            return False
        if self._contradicts_predicate(other):
            return True
        if not self.consistent_dimensionality(other):
            return False
        return self.excludes_other_quantity(other)

    def negated(self) -> Comparison:
        """Copy ``self``, with the opposite truth value."""
        return Comparison(
            template=self.content,
            truth=not self.truth,
            sign=self.sign,
            expression=self.expression,
        )

    def expression_comparison(self) -> str:
        """
        Convert text to a comparison with a quantity.

        :returns:
            string representation of a comparison with a
            quantity, which can include units due to the
            `pint <pint.readthedocs.io>`_  library.
        """

        if not self.expression:
            return ""
        comparison = self.sign or "="
        expand = {
            "==": "exactly equal to",
            "=": "exactly equal to",
            "!=": "not equal to",
            "<>": "not equal to",
            ">": "greater than",
            "<": "less than",
            ">=": "at least",
            "<=": "no more than",
        }
        return f"{expand[comparison]} {self.expression}"
