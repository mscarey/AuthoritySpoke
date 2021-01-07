r"""
Phrases that contain meanings of :class:`.Factor`\s, particularly :class:`.Fact`\s.

Can contain references to other :class:`.Factor`\s,
to numeric values, or to quantities (with the use of
the `pint <https://pint.readthedocs.io/en/0.9/>`_ library.)
"""

from __future__ import annotations

import re

from string import Template
from typing import ClassVar, Dict, Iterable
from typing import List, Optional, Sequence, Union

from pint import UnitRegistry

from authorityspoke.factors import Factor

ureg = UnitRegistry()
Q_ = ureg.Quantity


class StatementTemplate(Template):
    def __init__(self, template: str) -> None:
        super().__init__(template)
        self.make_content_singular()

    def make_content_singular(self) -> None:
        """Convert template text for self.context to singular "was"."""
        for placeholder in self.placeholders:
            bracketed = "{" + placeholder + "}"
            if bracketed in self.template:
                self.template = self.template.replace(
                    f"{bracketed} were", f"{bracketed} was"
                )
            else:
                self.template = self.template.replace(
                    f"{placeholder} were", f"{placeholder} was"
                )
        return None

    @property
    def placeholders(self) -> List[str]:
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


class Predicate:
    r"""
    A statement about real events or about a legal conclusion.

    Predicates may be "alleged" by a pleading, "supported" by evidence, or
    "found" to be factual by a jury verdict or a judge's finding of fact.

    :param content:
        a clause containing an assertion, with blanks represented
        by curly brackets showing where references to specific
        entities from the case can be inserted to make the clause specific.

    :param truth:
        indicates whether the clause in ``content`` is asserted to be
        true or false. ``None`` indicates an assertion as to "whether"
        the clause is true or false, without specifying which.

    :param reciprocal:
        if True, then the order of the first two entities
        is considered interchangeable. There's no way to make any entities
        interchangeable other than the first two.

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

    def __init__(
        self,
        template: str,
        truth: Optional[bool] = True,
        reciprocal: bool = False,
        comparison: str = "",
        quantity: Optional[Union[int, float, ureg.Quantity]] = None,
    ):
        """
        Clean up and test validity of attributes.

        If the :attr:`content` sentence is phrased to have a plural
        context factor, normalizes it by changing "were" to "was".
        """
        self.template = StatementTemplate(template)
        self.truth = truth
        self.reciprocal = reciprocal
        self.comparison = comparison
        self.quantity = quantity

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
            "truth={self.truth}, reciprocal={self.reciprocal}, "
            'comparison="{self.comparison}", quantity={self.quantity})'
        )

    @property
    def content(self) -> str:
        return self.template.template

    def content_without_placeholders(self) -> str:
        changes = {p: "{}" for p in self.template.placeholders}
        return self.template.substitute(**changes)

    def context_factors_mapping(
        self, context_factors: List[Factor]
    ) -> Dict[str, Factor]:
        placeholders = self.template.placeholders
        return dict(zip(placeholders, context_factors))

    def mapping_placeholder_to_string(self, context: List[Factor]) -> Dict[str, str]:
        mapping = self.context_factors_mapping(context)
        mapping_to_string = {k: v.short_string for k, v in mapping.items()}
        return mapping_to_string

    def phrase_with_context(self) -> str:
        mapping = self.mapping_placeholder_to_string()

        return self.predicate.template.substitute(**mapping)

    def content_with_entities(self, context: Union[Factor, Sequence[Factor]]) -> str:
        r"""
        Make a sentence by filling in ``self.content`` with generic :class:`.Factor`\s.

        :param context:
            generic :class:`.Factor`\s to be mentioned in the context of
            this Predicate. They do not need to be type :class:`.Entity`.

        :returns:
            a sentence created by substituting string representations
            of generic factors from a particular case into the return
            value of the :meth:`__str__` method.
        """

        if not isinstance(context, Iterable):
            context = (context,)
        if len(context) != len(self):
            raise ValueError(
                f"Exactly {len(self)} entities needed to complete "
                + f'"{self.content}", but {len(context)} were given.'
            )
        add_plurals = self.template.substitute(
            **self.mapping_placeholder_to_string(context)
        )

        with_plurals = Predicate.make_context_plural(
            sentence=add_plurals, context=context
        )
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

        if not (
            self.same_content_meaning(other) and self.reciprocal == other.reciprocal
        ):
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

    def means(self, other) -> bool:
        """
        Test whether ``self`` and ``other`` have identical meanings.

        To return ``True``, ``other`` can be neither broader nor narrower.
        """

        if not isinstance(other, self.__class__):
            return False

        if not self.same_content_meaning(other):
            return False

        if self.reciprocal != other.reciprocal or self.quantity != other.quantity:
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
            self.same_content_meaning(other) and self.reciprocal == other.reciprocal
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

        return len(set(self.template.placeholders))

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
            reciprocal=self.reciprocal,
            comparison=self.comparison,
            quantity=self.quantity,
        )

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

    @staticmethod
    def make_context_plural(sentence: str, context: Iterable[Factor]) -> str:
        """
        Replace "was" with "were" after a context slot in a sentence.

        TODO: move method somewhere where it belongs

        :param sentence:
            a sentence with pairs of curly braces representing slots for
            context factors

        :param index:
            the index of the context factor that is plural, counting
            from the start of the sentence

        :returns:
            a form of the sentence with one instance of "was" replaced
            with "were"
        """
        for factor in context:
            if factor.__dict__.get("name") and factor.__dict__.get("plural") is True:
                sentence = sentence.replace(f"{factor.name} was", f"{factor.name} were")
                sentence = sentence.replace(
                    f"{factor.name}> was", f"{factor.name}> were"
                )
        return sentence
