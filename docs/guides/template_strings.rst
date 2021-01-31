..  _template_strings:

Using Python Template Strings to Represent Legal Explanations
=============================================================

The AuthoritySpoke library provides you with Python classes that you can
use to represent a limited subset of English statements, so you can
create computable annotations representing aspects of legal reasoning and
factfinding. The interface for creating these phrases is similar to
`Predicate
logic <https://en.wikipedia.org/wiki/Category:Predicate_logic>`__: it
includes a Predicate, which is like a partial sentence with blank spaces
marked by placeholders. The placeholders can be replaced by nouns that
become the subjects or objects of this potential sentence.

I chose to implement this feature with :py:class:`string.Template`
instead of Python’s more powerful methods for inserting data into text
strings, such as `f-strings <https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals>`__
or the :py:meth:`str.format` method. The reason was
that template strings’ relative lack of versatility makes them more
predictable and less bug-prone. Template strings don’t execute any code
when they run, so they present less of a security problem and they can
be used with untrusted user-generated data.

Predicate objects
-----------------

Here’s an example of a template string used to create
a :class:`~authorityspoke.predicates.Predicate` object
in AuthoritySpoke version 0.5:

    >>> from authorityspoke import Predicate
    >>> parent_sentence = Predicate("$mother was ${child}'s parent")

The phrase that we passed to
the :class:`~authorityspoke.predicates.Predicate` constructor is used to create
a Python template string. `Template
strings <https://docs.python.org/3/library/string.html#string.Template>`__
are part of the Python standard library. The dollar signs and curly
brackets are special symbols used to indicate placeholders in Python’s
template string syntax.

Here’s an example of what happens when you provide a template string
with a mapping showing how to replace the placeholders with new text.

    >>> parent_sentence.template.substitute(mother="Ann", child="Bob")
    "Ann was Bob's parent"

Don’t worry: the use of the past tense doesn’t indicate that a tragedy
has befallen Ann or Bob. The :class:`~authorityspoke.predicates.Predicate` class
is designed to be used only
with an English-language phrase in the past tense. The past tense is
used because legal analysis is usually backward-looking, determining the
legal effect of past acts or past conditions. Don’t use capitalization
or end punctuation to signal the beginning or end of the phrase, because
the phrase may be used in a context where it’s only part of a longer
sentence.

Predicates can be compared using AuthoritySpoke’s :meth:`~authorityspoke.predicates.Predicate.means`\,
:meth:`~authorityspoke.predicates.Predicate.implies`\,
and :meth:`~authorityspoke.predicates.Predicate.contradicts` methods.
The :meth:`~authorityspoke.predicates.Predicate.means` method
checks whether one :class:`~authorityspoke.predicates.Predicate` has
the same meaning as another :class:`~authorityspoke.predicates.Predicate`\.
One reason for comparing Predicates using
the :meth:`~authorityspoke.predicates.Predicate.means` method instead
of Python’s ``==`` operator is
that the :meth:`~authorityspoke.predicates.Predicate.means` method can still
consider Predicates to have the same meaning even if they use different
identifiers for their placeholders.

    >>> another_parent_sentence = Predicate("$adult was ${kid}'s parent")
    >>> parent_sentence.template == another_parent_sentence.template
    False

    >>> another_parent_sentence.means(parent_sentence)
    True

You can also add a ``truth`` attribute to a Predicate to indicate
whether the statement described by the template is considered true or
false. AuthoritySpoke can then use that attribute to evaluate
relationships between the truth values of different Predicates
with the same template text. If you omit a ``truth`` parameter when
creating a Predicate, the default value is ``True``.

    >>> not_parent_sentence = Predicate("$adult was ${kid}'s parent", truth=False)
    >>> str(not_parent_sentence)
    "it was false that $adult was ${kid}'s parent"

    >>> parent_sentence.means(not_parent_sentence)
    False

    >>> parent_sentence.contradicts(not_parent_sentence)
    True


In the ``parent_sentence`` example above, there are really two different
placeholder formats. The first placeholder, ``mother``, is just preceded
by a dollar sign. The second placeholder, ``child``, is preceded by a
dollar sign and an open curly bracket, and followed by a closed curly
bracket. These formats aren’t specific to AuthoritySpoke; they’re part
of the Python standard library. The difference is that the format with
just the dollar sign can only be used for a placeholder that is
surrounded by whitespace. If the placeholder is next to some other
character, like an apostrophe, then you need to use the “braced” format
with the curly brackets. The placeholders themselves need to be valid
Python identifiers, which means they can only be made up of letters,
numbers, and underscores, and they can’t start with a number.
Docassemble users might already be familiar with these rules, since
Docassemble variables also have to be Python identifiers. Check out
Docassemble’s documentation for more `guidance on creating valid Python
identifiers <https://docassemble.org/docs/fields.html#variable%20names>`__.

Comparison objects
------------------

AuthoritySpoke’s :class:`~authorityspoke.predicates.Comparison` class
extends the concept of a
:class:`~authorityspoke.predicates.Predicate`\.
A :class:`~authorityspoke.predicates.Comparison` still contains a ``truth`` value and a
``template`` string, but that template should be used to identify a
quantity that will be compared to an ``expression`` using a ``sign``
such as an equal sign or a greater-than sign. This ``expression`` must
be a constant: either an integer, a floating point number, or a physical
quantity expressed in units that can be parsed using the `pint
library <https://pint.readthedocs.io/en/stable/defining-quantities.html#using-string-parsing>`__.
To encourage consistent phrasing, the template string in every
Comparison object must end with the word “was”. AuthoritySpoke will then
build the rest of the phrase using the comparison sign and expression
that you provide.

Comparisons with Measurements and Units
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use a measurement as a Comparison’s ``expression``, pass the measurement as
a string when constructing the Comparison object, and it will be converted to a :class:`pint.Quantity`\.

    >>> from authorityspoke import Comparison
    >>> drug_comparison = Comparison(
    >>>     "the weight of marijuana that $defendant possessed was",
    >>>     sign=">=",
    >>>     expression="0.5 kilograms")
    >>> str(drug_comparison)
    'that the weight of marijuana that $defendant possessed was at least 0.5 kilogram'


(The pint library always uses singular nouns for units like “kilogram”,
when rendering them as text.)

By making the quantitative part of the phrase explicit, you make it
possible for AuthoritySpoke to consider quantities when checking whether
one Comparison :meth:`~authorityspoke.predicates.Comparison.implies` or
:meth:`~authorityspoke.predicates.Comparison.contradicts` another.

    >>> smaller_drug_comparison = Comparison(
    >>>     "the weight of marijuana that $defendant possessed was",
    >>>     sign=">=",
    >>>     expression="250 grams")
    >>> str(smaller_drug_comparison)
    'that the weight of marijuana that $defendant possessed was at least 250 gram'

AuthoritySpoke will understand that if the weight was at least 0.5
kilograms, that implies it was also at least 250 grams.

    >>> drug_comparison.implies(smaller_drug_comparison)
    True

If you phrase a :class:`~authorityspoke.predicates.Comparison` with an
inequality sign using ``truth=False``, AuthoritySpoke will silently
modify your statement so
it can have ``truth=True`` with a different sign. In this example, the
user’s input indicates that it’s false that the weight of the marijuana
was more than 10 grams. AuthoritySpoke interprets this to mean it’s true
that the weight was no more than 10 grams.

    >>> drug_comparison_with_upper_bound = Comparison(
    >>>     "the weight of marijuana that $defendant possessed was",
    >>>     sign=">",
    >>>     expression="10 grams",
    >>>     truth=False)
    >>> str(drug_comparison_with_upper_bound)
    'that the weight of marijuana that $defendant possessed was no more than 10 gram'


Of course, this Comparison :meth:`~authorityspoke.predicates.Comparison.contradicts`
the other Comparisons that
asserted the weight was much greater.

    >>> drug_comparison_with_upper_bound.contradicts(drug_comparison)
    True

The unit that the Comparison parses doesn't have to be weight. It could also be distance, time, volume,
units of surface area such as square kilometers or acres, or units that combine multiple dimensions
such as miles per hour or meters per second.

Comparisons with Integer and Float Expressions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the number needed for
a :class:`~authorityspoke.predicates.Comparison` isn’t a
physical :class:`~pint.quantity.Quantity` that
can be described with the units in the `pint
library <https://pint.readthedocs.io/en/stable/>`__, you should
phrase the text in the template string to explain what the number
describes. The template string will still need to end with the word
“was”. The value of the expression parameter should be an integer or a
floating point number, not a string to be parsed.

    >>> three_children = Comparison(
    >>>     "the number of children in ${taxpayer}'s household was",
    >>>     sign="=",
    >>>     expression=3)
    >>> str(three_children)
    "that the number of children in ${taxpayer}'s household was exactly equal to 3"

The numeric expression will still be available for comparison methods
like :meth:`~authorityspoke.predicates.Comparison.implies`
or :meth:`~authorityspoke.predicates.Comparison.contradicts`\,
but no unit conversion will be available.

    >>> at_least_two_children = Comparison("the number of children in ${taxpayer}'s household was", sign=">=", expression=2)
    >>> three_children.implies(at_least_two_children)
    True

Floating point comparisons work similarly.

    >>> specific_tax_rate = Comparison("${taxpayer}'s marginal income tax rate was", sign="=", expression=.3)
    >>> tax_rate_over_25 = Comparison("${taxpayer}'s marginal income tax rate was", sign=">", expression=.25)
    >>> specific_tax_rate.implies(tax_rate_over_25)
    True


Comparisons with Dates
~~~~~~~~~~~~~~~~~~~~~~

The ``expression`` field of
a :class:`~authorityspoke.predicates.Comparison` can be a :py:class:`datetime.date`\.

    >>> from datetime import date
    >>> copyright_date_range = Comparison("the date when $work was created was", sign=">=", expression = date(1978,1,1))
    >>> str(copyright_date_range)
    'that the date when $work was created was at least 1978-01-01'


And :py:class:`~datetime.date`\s and :py:class:`~datetime.date` ranges can be compared with each other,
similar to how numbers can be compared to number ranges.

    >>> copyright_date_specific = Comparison("the date when $work was created was", sign="=", expression = date(1980,6,20))
    >>> copyright_date_specific.implies(copyright_date_range)
    True

Using Entities as Context Terms
-------------------------------

AuthoritySpoke isn’t limited to
comparing :class:`~authorityspoke.predicates.Predicate`\s
and :class:`~authorityspoke.predicates.Comparison`\s
containing unassigned placeholder text. You can
use :class:`~authorityspoke.statements.entities.Entity` objects to
assign specific terms to the placeholders. You then link the terms to
the :class:`~authorityspoke.predicates.Predicate`
or :class:`~authorityspoke.predicates.Comparison` inside
a :class:`~authorityspoke.facts.Fact` object.

    >>> from authorityspoke import Entity, Fact
    >>> ann = Entity("Ann", generic=False)
    >>> claude = Entity("Claude", generic=False)
    >>> ann_tax_rate = Fact(specific_tax_rate, terms=ann)
    >>> claude_tax_rate = Fact(tax_rate_over_25, terms=claude)
    >>> str(ann_tax_rate)
    "the fact that Ann's marginal income tax rate was exactly equal to 0.3"

    >>> str(claude_tax_rate)
    "the fact that Claude's marginal income tax rate was greater than 0.25"


Before, we saw that the Comparison ``specific_tax_rate``
:meth:`~authorityspoke.predicates.Comparison.implies`
``tax_rate_over_25``. But when we have a fact about the tax rate of a
specific person named Ann, it doesn’t imply anything about Claude’s tax
rate.

    >>> ann_tax_rate.implies(claude_tax_rate)
    False

That seems to be the right answer in this case. But sometimes, in legal
reasoning, we want to refer to people in a generic sense. We might want
to say that a statement about one person can imply a statement about a
different person, because most legal rulings can be generalized to apply
to many different people regardless of exactly who those people are. To
illustrate that idea, let’s create two “generic” people and show that a
Fact about one of them implies a Fact about the other.

    >>> devon = Entity("Devon", generic=True)
    >>> elaine = Entity("Elaine", generic=True)
    >>> devon_tax_rate = Fact(specific_tax_rate, terms=devon)
    >>> elaine_tax_rate = Fact(tax_rate_over_25, terms=elaine)
    >>> devon_tax_rate.implies(elaine_tax_rate)
    True

In the string representations of :class:`~authorityspoke.facts.Fact`\s, generic Entities are shown in
angle brackets as a reminder that they may be considered to correspond
to different Entities when being compared to other objects.

    >>> str(devon_tax_rate)
    "the fact that <Devon>'s marginal income tax rate was exactly equal to 0.3"

    >>> str(elaine_tax_rate)
    "the fact that <Elaine>'s marginal income tax rate was greater than 0.25"


When the :meth:`~authorityspoke.predicates.Comparison.implies` method
produces the answer ``True``, we can also
use the :meth:`~authorityspoke.comparisons.Comparable.explain_implication`
method to find out which pairs of
generic terms can be considered analagous to one another.

    >>> explanation = devon_tax_rate.explain_implication(elaine_tax_rate)
    >>> str(explanation)
    'ContextRegister(<Devon> is like <Elaine>)'


Identical Terms
---------------

If for some reason you need to mention the same term more than once in a
Predicate or Comparison, use the same placeholder for that term each
time. When you provide a sequence of terms for the Fact object using
that Predicate, only include each unique term once. The terms should be
listed in the same order that they first appear in the template text.

    >>> opened_account = Fact(
    >>>     Predicate("$applicant opened a bank account for $applicant and $cosigner"),
    >>>     terms=(devon, elaine))
    >>> str(opened_account)
    'the fact that <Devon> opened a bank account for <Devon> and <Elaine>'


Interchangeable Terms
---------------------

Sometimes, a Predicate or Comparison needs to mention two terms that are
different from each other, but that have interchangeable positions in
that particular phrase. To convey interchangeability, the template
string should use identical text for the placeholders for the
interchangeable terms, except that the different placeholders should
each end with a different digit.

    >>> ann = Entity("Ann", generic=False)
    >>> bob = Entity("Bob", generic=False)
    >>> ann_and_bob_were_family = Fact(
    >>>     predicate=Predicate("$relative1 and $relative2 both were members of the same family"),
    >>>     terms=(ann, bob))
    >>> bob_and_ann_were_family = Fact(
    >>>     predicate=Predicate("$relative1 and $relative2 both were members of the same family"),
    >>>     terms=(bob, ann))
    >>> str(ann_and_bob_were_family)
    'the fact that Ann and Bob both were members of the same family'

    >>> str(bob_and_ann_were_family)
    'the fact that Bob and Ann both were members of the same family'

    >>> ann_and_bob_were_family.means(bob_and_ann_were_family)
    True

If you create a :class:`~authorityspoke.facts.Fact` using placeholders
that don’t fit the pattern of being identical
except for a final digit, then transposing two non-generic terms will
change the meaning of the Fact.

    >>> parent_sentence = Predicate("$mother was ${child}'s parent")
    >>> ann_is_parent = Fact(parent_sentence, terms = (ann, bob))
    >>> bob_is_parent = Fact(parent_sentence, terms = (bob, ann))
    >>> str(ann_is_parent)
    "the fact that Ann was Bob's parent"

    >>> str(bob_is_parent)
    "the fact that Bob was Ann's parent"

    >>> ann_is_parent.means(bob_is_parent)
    False



Higher-Order Predicates
-----------------------

In AuthoritySpoke, terms referenced by a Predicate or Comparison can
contain references to Facts as well as Entities. That mean they can
include the text of other Predicates. This feature is intended for
incorporating references to what people said, knew, or believed.

    >>> statement = Predicate("$speaker told $listener $event")
    >>> bob_had_drugs = Fact(smaller_drug_comparison, terms=bob)
    >>> bob_told_ann_about_drugs = Fact(statement, terms=(bob, ann, bob_had_drugs))
    >>> str(bob_told_ann_about_drugs)
    'the fact that Bob told Ann the fact that the weight of marijuana that Bob possessed was at least 250 gram'

A higher-order Predicate can be used to establish that one Fact implies
another. In legal reasoning, it’s common to accept that if a person knew
or communicated something, then the person also knew or communicated any
facts that are obviously implied by what the person actually knew or
said. In this example, the fact that Bob told Ann he possessed more than
0.5 kilograms means he also told Ann that he possessed more than 250
grams.

    >>> bob_had_more_drugs = Fact(drug_comparison, terms=bob)
    >>> bob_told_ann_about_more_drugs = Fact(statement, terms=(bob, ann, bob_had_more_drugs))
    >>> str(bob_told_ann_about_more_drugs)
    'the fact that Bob told Ann the fact that the weight of marijuana that Bob possessed was at least 0.5 kilogram'

    >>> bob_told_ann_about_more_drugs.implies(bob_told_ann_about_drugs)
    True


However, a contradiction between Facts referenced in higher-order
Predicates doesn’t cause the first-order Facts to contradict one
another. For example, it’s not contradictory to say that a person
has said two contradictory things.

    >>> bob_had_less_drugs = Fact(drug_comparison_with_upper_bound, terms=bob)
    >>> bob_told_ann_about_less_drugs = Fact(statement, terms=(bob, ann, bob_had_less_drugs))
    >>> str(bob_told_ann_about_less_drugs)
    'the fact that Bob told Ann the fact that the weight of marijuana that Bob possessed was no more than 10 gram'

    >>> bob_told_ann_about_less_drugs.contradicts(bob_told_ann_about_more_drugs)
    False


Higher-order Facts can refer to terms that weren’t referenced by the
first-order Fact. AuthoritySpoke will recognize that the use of
different terms in the second-order Fact changes the meaning of the
first-order Fact.

    >>> claude_had_drugs = Fact(smaller_drug_comparison, terms=claude)
    >>> bob_told_ann_about_claude = Fact(statement, terms=(bob, ann, claude_had_drugs))
    >>> str(bob_told_ann_about_claude)
    'the fact that Bob told Ann the fact that the weight of marijuana that Claude possessed was at least 250 gram'

    >>> bob_told_ann_about_drugs.implies(bob_told_ann_about_claude)
    False
