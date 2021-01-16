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
from typing import ClassVar, Dict, Iterable, Iterator
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
        Count bracket pairs in ``self.content``, minus 1 if ``self.quantity==True``.

        :returns:
            the number of context :class:`.Factor`\s that must be
            specified to fill in the blanks in ``self.content``.
        """

        placeholders = [
            m.group("named") or m.group("braced")
            for m in self.pattern.finditer(self.template)
            if m.group("named") or m.group("braced")
        ]
        return placeholders

    def _check_number_of_terms(
        self, placeholders: List[str], context: Sequence[Factor]
    ) -> None:
        if len(placeholders) != len(context):
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

    :param content:
        a clause containing an assertion in English in the past tense, with
        placeholders showing where references to specific
        :class:`~authorityspoke.factors.Factor`\s
        from the case can be inserted to make the clause specific.
        This string must be a valid Python :py:class:`string.Template`\.

    :param truth:
        indicates whether the clause in ``content`` is asserted to be
        true or false. ``None`` indicates an assertion as to "whether"
        the clause is true or false, without specifying which.

    :param comparison:
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
        may contain no more than one ``comparison`` and one ``quantity``.
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

    @classmethod
    def read_quantity(
        cls, value: Union[float, int, str]
    ) -> Union[float, int, ureg.Quantity]:
        """
        Create pint quantity object from text.

        See `pint tutorial <https://pint.readthedocs.io/en/0.9/tutorial.html>`_

        :param quantity:
            when a string is being parsed for conversion to a
            :class:`Predicate`, this is the part of the string
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

    def __init__(
        self,
        template: str,
        truth: Optional[bool] = True,
        comparison: str = "",
        quantity: Optional[Union[int, float, ureg.Quantity]] = None,
    ):
        """
        Clean up and test validity of attributes.

        If the :attr:`content` sentence is phrased to have a plural
        context factor, normalizes it by changing "were" to "was".
        """
        self.template = StatementTemplate(template, make_singular=True)
        self.truth = truth
        self.comparison = comparison
        self.quantity = self.read_quantity(quantity)

        if self.comparison and self.comparison not in self.opposite_comparisons.keys():
            raise ValueError(
                f'"comparison" string parameter must be one of {self.opposite_comparisons.keys()}.'
            )

        if self.comparison and self.truth is False:
            self.truth = True
            self.comparison = self.opposite_comparisons[self.comparison]

        if self.quantity is not None and not self.content.endswith("was"):
            raise ValueError(
                "If a Predicate includes a quantity, its 'content' must end "
                "with the word 'was' to signal the comparison with the quantity. "
                f"The word 'was' is not the end of the string '{self.content}'."
            )

    def __repr__(self):
        return (
            f'Predicate(template="{self.template.template}", '
            "truth={self.truth}, "
            'comparison="{self.comparison}", quantity={self.quantity})'
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

    def consistent_dimensionality(self, other: Predicate) -> bool:
        """Test if ``other`` has a quantity parameter consistent with ``self``."""

        if isinstance(self.quantity, ureg.Quantity):
            if not isinstance(other.quantity, ureg.Quantity):
                return False
            if self.quantity.dimensionality != other.quantity.dimensionality:
                return False
        elif isinstance(other.quantity, ureg.Quantity):
            return False
        return True

    def contradicts(self, other: Optional[Predicate]) -> bool:
        r"""
        Test whether ``other`` and ``self`` have contradictory meanings.

        This first tries to find a contradiction based on the relationship
        between the quantities in the :class:`Predicate`\s. If there are
        no quantities, it returns ``False`` only if the content is exactly
        the same and ``self.truth`` is different.
        """
        if other is None:
            return False

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + f"contradiction with other {self.__class__} objects or None."
            )

        if self.truth is None or other.truth is None:
            return False

        if not self.consistent_dimensionality(other):
            return False

        if not (self.same_content_meaning(other) and self.same_term_positions(other)):
            return False

        if self.quantity and other.quantity:
            return self.excludes_other_quantity(other)
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

    def means(self, other) -> bool:
        """
        Test whether ``self`` and ``other`` have identical meanings.

        To return ``True``, ``other`` can be neither broader nor narrower.
        """

        if not isinstance(other, self.__class__):
            return False

        if not self.same_content_meaning(other):
            return False

        if not self.same_term_positions(other):
            return False

        if self.quantity != other.quantity:
            return False

        return self.truth == other.truth and self.comparison == other.comparison

    def __gt__(self, other: Optional[Predicate]) -> bool:
        """
        Test whether ``self`` implies ``other``.

        :returns:
            whether ``self`` implies ``other``, which is ``True``
            if their statements about quantity imply it.
        """
        return self.implies(other)

    def implies(self, other: Optional[Predicate]) -> bool:
        """
        Test whether ``self`` implies ``other``.

        :returns:
            whether ``self`` implies ``other``, which is ``True``
            if their statements about quantity imply it.
        """
        if other is None:
            return True
        if not isinstance(other, self.__class__):
            raise TypeError(
                f"{self.__class__} objects may only be compared for "
                + f"implication with other {self.__class__} objects or None."
            )

        # Assumes no predicate implies another based on meaning of their content text
        if not (
            self.same_content_meaning(other)
            and self.term_index_permutations() == other.term_index_permutations()
        ):
            return False

        if other.truth is None:
            return True

        if self.truth is None:
            return False

        if not (
            self.quantity and other.quantity and self.comparison and other.comparison
        ):
            return False

        return self.includes_other_quantity(other)

    def __ge__(self, other: Predicate) -> bool:
        if self.means(other):
            return True
        return self.implies(other)

    def excludes_other_quantity(self, other: Predicate) -> bool:
        """Test if quantity ranges in self and other are non-overlapping."""
        if (
            not self.quantity
            or not other.quantity
            or not self.consistent_dimensionality(other)
        ):
            return False

        if self.quantity > other.quantity:
            if "<" not in self.comparison and ">" not in other.comparison:
                return True
        if self.quantity < other.quantity:
            if ">" not in self.comparison and "<" not in other.comparison:
                return True
        return self.quantity == other.quantity and (
            ("=" in self.comparison) != ("=" in other.comparison)
        )

    def includes_other_quantity(self, other: Predicate) -> bool:
        """Test if the range of quantities mentioned in self is a subset of other's."""
        if not self.quantity or not other.quantity:
            return bool(self.quantity)

        if not self.consistent_dimensionality(other):
            return False

        if (
            (self.quantity < other.quantity)
            and ("<" in self.comparison or "=" in self.comparison)
            and ("<" in other.comparison)
        ):
            return True
        if (
            (self.quantity > other.quantity)
            and (">" in self.comparison or "=" in self.comparison)
            and (">" in other.comparison)
        ):
            return True
        if "=" in self.comparison:
            if ("<" in other.comparison and self.quantity < other.quantity) or (
                ">" in other.comparison and self.quantity > other.quantity
            ):
                return True
        return self.quantity == other.quantity and (
            ("=" in self.comparison) == ("=" in other.comparison)
        )

    def __len__(self):
        """
        Also called the linguistic valency, arity, or adicity.

        :returns:
            the number of entities that can fit in the pairs of brackets
            in the predicate. ``self.quantity`` doesn't count as one of these entities,
            even though the place where ``self.quantity`` goes in represented by brackets
            in the ``self.content`` string.
        """

        return len(set(self.template.get_placeholders()))

    def quantity_comparison(self) -> str:
        """
        Convert text to a comparison with a quantity.

        :returns:
            string representation of a comparison with a
            quantity, which can include units due to the
            `pint <pint.readthedocs.io>`_  library.
        """

        if not self.quantity:
            return ""
        comparison = self.comparison or "="
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
        return f"{expand[comparison]} {self.quantity}"

    def negated(self) -> Predicate:
        """Copy ``self``, with the opposite truth value."""
        return Predicate(
            template=self.content,
            truth=not self.truth,
            comparison=self.comparison,
            quantity=self.quantity,
        )

    def term_positions(self):
        """
        Create list of positions that each term could take without changing Predicate's meaning.

        Assumes that if placeholders are the same except for a final digit, that means
        they've been labeled as interchangeable with one another.
        """

        placeholders = self.template.get_placeholders()
        without_duplicates = list(dict.fromkeys(placeholders))
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
        if self.quantity:
            full_content = f"{content} {self.quantity_comparison()}"
        else:
            full_content = content
        return f"{truth_prefix}{full_content}"

    def __str__(self):
        return self.add_truth_to_content(self.content)
