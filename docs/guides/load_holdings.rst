..  _create_holding_data:

Creating and Loading Holding Data
=================================

This tutorial will show how to load objects representing judicial
holdings into AuthoritySpoke. First we'll see how to create an instance
of the :class:`~authorityspoke.holdings.Holding` class using Python
commands in a Python shell or notebook.

The case we'll be using for this demonstration is United States v.
Mazza-Alaluf, `621 F.3d
205 <https://www.courtlistener.com/opinion/175697/united-states-v-mazza-alaluf/>`__
This is a 2010 case from the Court of Appeals for the Second Circuit. It
describes how a violation of a state's licensing requirement for money
transmitting businesses can result in a felony conviction under federal
law.

We'll start by loading a copy of the judicial opinion from Harvard's
Caselaw Access Project (CAP). AuthoritySpoke includes a download client
for getting these opinions. To download full cases from CAP, you'll need
to `register for a CAP API key <https://case.law/user/register/>`__.
Once you have an API key, you can make it available as an environment
variable by saving it as a file called ``.env``. This process is
described in the `python-dotenv
documentation <https://saurabh-kumar.com/python-dotenv/#getting-started>`__.

    >>> from datetime import date
    >>> import os
    >>> from dotenv import load_dotenv
    >>> load_dotenv(".env")
    True
    >>> CAP_API_KEY = os.getenv('CAP_API_KEY')
    >>> USE_REAL_CASE_API = False

Next, we'll create a :class:`~authorityspoke.io.downloads.CAPClient` object,
which is a download client for
getting decisions from the Caselaw Access Project. It has methods to
:meth:`~authorityspoke.io.downloads.CAPClient.fetch` decisions,
which means to get them in standard JSON format, and
also methods to :meth:`~authorityspoke.io.downloads.CAPClient.read`
decisions, which means to fetch them and then
convert them into AuthoritySpoke :class:`~justopinion.decisions.Decision` objects. Since we know the
citation of the case we want, we'll use the :meth:`~authorityspoke.io.downloads.CAPClient.read_cite` method.

    >>> from authorityspoke.io import CAPClient
    >>> from authorityspoke.decisions import DecisionReading, Decision, Opinion, CAPCitation
    >>> if USE_REAL_CASE_API:
    ...     client = CAPClient(api_token=CAP_API_KEY)
    ...     licensing_case = client.read_cite(
    ...         cite="621 F.3d 205",
    ...        full_case=False)
    ... else:
    ...     licensing_case = Decision(
    ...        decision_date=date(2010,9,22),
    ...        name_abbreviation="United States v. Mazza-Alaluf",
    ...        citations=[CAPCitation(cite="621 F.3d 205")])
    ...     licensing_case.add_opinion(Opinion())
    >>> print(licensing_case)
    United States v. Mazza-Alaluf, 621 F.3d 205 (2010-09-22)

If we had used ``full_case=True``, we would have the option to view the full
text of the majority opinion using the command ``licensing_case.majority.text``.


Creating Holdings with Python
-----------------------------

Now we'll try creating a :class:`~authorityspoke.holdings.Holding` from the Mazza-Alaluf case using Python
commands. One main idea from this case is that certain violations of
state law can establish an element of a federal criminal offense called
"conducting a money transmitting business without a license required by
state law". To model this concept in AuthoritySpoke we need to frame it in
procedural terms. In the context of a litigation process, the Holding tells us
something about how one factual finding can lead to another.

    >>> from authorityspoke import Entity, Fact, Holding
    >>> new_york_offense = Fact(
    ...     predicate="{defendant} used {defendant}'s business {business} to commit the New York offense "
    ...     "of engaging in the business of receiving money "
    ...     "for transmission or transmitting the same, without a license therefor",
    ...     terms=[Entity(name="Mazza-Alaluf"), Entity(name="Turismo Costa Brava")])
    >>> no_appropriate_state_license = Fact(
    ...     predicate=("{defendant} operated {business} without an appropriate money transmitting "
    ...     "license in a State where such operation was punishable as a misdemeanor "
    ...     "or a felony under State law"),
    ...     terms=[Entity(name="Mazza-Alaluf"), Entity(name="Turismo Costa Brava")])
    >>> new_york_holding = Holding.from_factors(
    ...     inputs=new_york_offense,
    ...     outputs=no_appropriate_state_license,
    ...     universal=True)
    >>> print(new_york_holding)
    the Holding to ACCEPT
      the Rule that the court MAY ALWAYS impose the
        RESULT:
          the fact that <Mazza-Alaluf> operated <Turismo Costa Brava> without an
          appropriate money transmitting license in a State where such operation
          was punishable as a misdemeanor or a felony under State law
        GIVEN:
          the fact that <Mazza-Alaluf> used <Mazza-Alaluf>'s business <Turismo
          Costa Brava> to commit the New York offense of engaging in the
          business of receiving money for transmission or transmitting the same,
          without a license therefor


There's still something missing from the object we're calling
``new_york_holding``. We need an object that represents the statute
being interpreted by the court. To get that, we're going to use the
Legislice API, so we're going to need an API :class:`~legislice.download.Client` class, imported as
:class:`~authorityspoke.io.downloads.LegisClient`\. While
:class:`~authorityspoke.io.downloads.CAPClient` was for getting court opinions,
:class:`~authorityspoke.io.downloads.LegisClient`  is for getting legislation. Once again we need to `sign
up for an API token <https://authorityspoke.com/account/signup/>`__,
then save that API token in the ``.env`` file, and then load the API
token using `dotenv <https://saurabh-kumar.com/python-dotenv/#getting-started>`__.

    >>> from authorityspoke import LegisClient
    >>> LEGISLICE_API_TOKEN = os.getenv("LEGISLICE_API_TOKEN")
    >>> LEGIS_CLIENT = LegisClient(api_token=LEGISLICE_API_TOKEN)

Now we can use the :class:`~authorityspoke.io.downloads.LegisClient` to
:meth:`~legislice.download.Client.read` statutes from the United
States Code. We do this by specifying a URL-like path to the statute we
want. (These path identifiers are also used by the US government's
United States Legislative Markup format.) Here, we want part of
United States Code title 18, section 1960(b)(1). The path to that
provision is "/us/usc/t18/s1960/b/1".

    >>> definition_statute = LEGIS_CLIENT.read("/us/usc/t18/s1960/b/1")
    >>> print(definition_statute)
    /us/usc/t18/s1960/b/1 (2013-07-18)
    >>> definition_statute.text[:99]
    'the term “unlicensed money transmitting business” means a money transmitting business which affects'

We don't have to use the entire text of this statute provision. Instead
we can :meth:`~legislice.enactments.Enactment.select` just the part of the text we want. Using the ``end``
parameter, we can indicate that we want everything through the string
we've identified as the ``end``, but that we don't want anything past
that.

    >>> felony_passage = definition_statute.select(
    ...     end="or a felony under State law")

One way to add this Enactment to the Holding is by using the addition
operator (the plus sign).

    >>> holding_from_python = new_york_holding + felony_passage
    >>> print(holding_from_python)
    the Holding to ACCEPT
      the Rule that the court MAY ALWAYS impose the
        RESULT:
          the fact that <Mazza-Alaluf> operated <Turismo Costa Brava> without an
          appropriate money transmitting license in a State where such operation
          was punishable as a misdemeanor or a felony under State law
        GIVEN:
          the fact that <Mazza-Alaluf> used <Mazza-Alaluf>'s business <Turismo
          Costa Brava> to commit the New York offense of engaging in the
          business of receiving money for transmission or transmitting the same,
          without a license therefor
        GIVEN the ENACTMENT:
          "the term “unlicensed money transmitting business” means a money transmitting business which affects interstate or foreign commerce in any manner or degree and— is operated without an appropriate money transmitting license in a State where such operation is punishable as a misdemeanor or a felony under State law…" (/us/usc/t18/s1960/b/1 2013-07-18)


Now we've created a computable model of a judicial holding with Python.


Combining Holdings
--------------------------

Now let's load another Holding about the same case from AuthoritySpoke's
``examples`` package. We'll use an :class:`~authorityspoke.opinions.AnchoredHoldings`
object that includes Holdings and their text anchors.

  >>> from authorityspoke.examples import mazza as mazza_example
  >>> holdings_with_anchors = mazza_example.anchored_holdings()
  >>> holding_from_examples = holdings_with_anchors.holdings[1].holding

Next, we'll print the holding we loaded to see how AuthoritySpoke
interpreted the structured example data.

  >>> print(holding_from_examples)
  the Holding to ACCEPT
    the Rule that the court MUST ALWAYS impose the
      RESULT:
        the fact that <Mazza-Alaluf> committed the offense of conducting a
        money transmitting business without a license required by state law
      GIVEN:
        the fact that <Mazza-Alaluf> operated <Turismo Costa Brava> without an
        appropriate money transmitting license in a State where such operation
        was punishable as a misdemeanor or a felony under State law
        the fact that <Mazza-Alaluf> operated <Turismo Costa Brava> as a
        business
        the fact that <Turismo Costa Brava> was a money transmitting business
      DESPITE:
        the fact it was false that <Turismo Costa Brava> was a domestic
        financial institution
      GIVEN the ENACTMENT:
        "…is operated without an appropriate money transmitting license in a State where such operation is punishable as a misdemeanor or a felony under State law, whether or not the defendant knew that the operation was required to be licensed or that the operation was so punishable…" (/us/usc/t18/s1960/b/1 2013-07-18)
      DESPITE the ENACTMENT:
        ""domestic financial agency" and "domestic financial institution" apply to an action in the United States of a financial agency or institution." (/us/usc/t31/s5312/b/1 2013-07-18)


The Holding that we created in Python and the Holding that we loaded from
the examples package are both valid AuthoritySpoke objects. We can demonstrate this by
adding the two Holdings together to make a combined Holding that uses
information from both of them.

  >>> combined_holding = holding_from_python + holding_from_examples
  >>> print(combined_holding)
  the Holding to ACCEPT
    the Rule that the court MAY ALWAYS impose the
      RESULT:
        the fact that <Mazza-Alaluf> committed the offense of conducting a
        money transmitting business without a license required by state law
        the fact that <Mazza-Alaluf> operated <Turismo Costa Brava> without an
        appropriate money transmitting license in a State where such operation
        was punishable as a misdemeanor or a felony under State law
      GIVEN:
        the fact that <Mazza-Alaluf> operated <Turismo Costa Brava> as a
        business
        the fact that <Turismo Costa Brava> was a money transmitting business
        the fact that <Mazza-Alaluf> used <Mazza-Alaluf>'s business <Turismo
        Costa Brava> to commit the New York offense of engaging in the
        business of receiving money for transmission or transmitting the same,
        without a license therefor
      DESPITE:
        the fact it was false that <Turismo Costa Brava> was a domestic
        financial institution
      GIVEN the ENACTMENTS:
        "…is operated without an appropriate money transmitting license in a State where such operation is punishable as a misdemeanor or a felony under State law, whether or not the defendant knew that the operation was required to be licensed or that the operation was so punishable…" (/us/usc/t18/s1960/b/1 2013-07-18)
        "the term “unlicensed money transmitting business” means a money transmitting business which affects interstate or foreign commerce in any manner or degree and— is operated without an appropriate money transmitting license in a State where such operation is punishable as a misdemeanor or a felony under State law…" (/us/usc/t18/s1960/b/1 2013-07-18)
      DESPITE the ENACTMENT:
        ""domestic financial agency" and "domestic financial institution" apply to an action in the United States of a financial agency or institution." (/us/usc/t31/s5312/b/1 2013-07-18)


By combining the two Holdings, AuthoritySpoke has inferred that the :class:`~authorityspoke.facts.Fact`
that a defendant has committed the New York offense can substitute for the
Fact that the defendant operated "without an appropriate money
transmitting license in a State where such operation was punishable as a
misdemeanor or a felony under State law". If the former Fact is
available, then the offense can be established even if the latter Fact
hasn't been found yet.

Now that we generated this :class:`~authorityspoke.opinions.AnchoredHoldings` object
containing the example holding data, we can link the :class:`~authorityspoke.holdings.Holding`\s
to the :class:`~justopinion.decisions.Decision` with
a :class:`~authorityspoke.decisions.DecisionReading` object.
While a :class:`~justopinion.decisions.Decision` is a record of what a court actually published,
a :class:`~authorityspoke.decisions.DecisionReading` represents the user's "reading" of the Decision.
The DecisionReading indicates what Holdings are supported by the Decision,
as well as what text passages support each Holding.

We'll use the :meth:`~authorityspoke.decisions.Decision.posit` method to
link the Holdings to the Decision. Then we can verify that those two Holdings
are now considered the two holdings of the Decision.

    >>> licensing_case_reading = DecisionReading(decision=licensing_case)
  >>> licensing_case_reading.posit(holdings_with_anchors)
    >>> len(licensing_case_reading.holdings)
    2
