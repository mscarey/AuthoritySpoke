..  _statute_rules:

Legislative Rule Models with AuthoritySpoke
===========================================

This tutorial will show how to use
`AuthoritySpoke <https://authorityspoke.readthedocs.io/en/latest/>`__ to
model legal rules found in legislation. This is a departure from most of
the AuthoritySpoke documentation, which focuses on judicial holdings.

These examples are based on the fictional `Australian Beard Tax
(Promotion of Enlightenment Values) Act
1934 <https://github.com/ServiceInnovationLab/example-rules-as-code>`__,
which was created thanks to the New Zealand `Service Innovation
Lab <https://github.com/ServiceInnovationLab>`__, to supply test data
for experimental legal rule automation systems.

The Service Innovation Lab’s version of the Beard Tax Act is `a
PDF <https://github.com/ServiceInnovationLab/example-rules-as-code/blob/master/legislation.pdf>`__.
AuthoritySpoke is designed to load legislation from JSON data using a
related Python library called
`Legislice <https://github.com/mscarey/legislice>`__. So I’ve set up a
web API that can serve the provisions of the Beard Act. You can also
`browse the provisions <https://authorityspoke.com/legislice/test/>`__
of the Beard Act in your web browser.

For convenience, this tutorial will use AuthoritySpoke's fake testing
client with fake JSON responses, instead of connecting to the real API.

    >>> import json
    >>> import os
    >>> from authorityspoke.io.fake_enactments import FakeClient
    >>> legis_client = FakeClient.from_file("beard_act.json")

Next, I’ll prepare annotations for the statute provisions in a JSON
file, and then load them as a Python dictionary. AuthoritySpoke rules
are procedural, so they have one or more outputs, and zero or more
inputs. They can also have “despite” factors, which are factors that may
not support the output, but they don’t preclude the output either.

AuthoritySpoke rules are usually supported by enactments such as statute
sections. These can be retrieved from the API with the URI-like
identifiers like those in United States Legislative Markup (USLM). In
this case, since the Beard Tax Act is Act 47 of 1934, the identifier for
Section 4 of the Act is
`/test/acts/47/4 <https://authorityspoke.com/legislice/test/acts/47/4@2035-08-01>`__.

In AuthoritySpoke, you have to think about two JSON schemas: there’s one
schema for legislative provisions fetched from the web API, and another
schema for rule annotations that you (currently) have to create for
yourself. Of course, you can create either type of object directly in
Python instead of loading them from a JSON file. For details, see the
`AuthoritySpoke reference
manual <https://authorityspoke.readthedocs.io/en/latest/>`__. Here’s an
example of one JSON rule annotation.

    >>> from pprint import pprint
    >>> from authorityspoke.io import loaders
    >>> beard_dictionary = loaders.load_holdings("beard_rules.yaml")
    >>> pprint(beard_dictionary[0], sort_dicts=False)
    {'inputs': [{'type': 'fact',
                 'content': '{the suspected beard} was facial hair'},
                {'type': 'fact',
                 'content': 'the length of the suspected beard was >= 5 '
                            'millimetres'},
                {'type': 'fact',
                 'content': 'the suspected beard occurred on or below the chin'}],
     'outputs': [{'type': 'fact',
                  'content': 'the suspected beard was a beard',
                  'name': 'the fact that the facial hair was a beard'}],
     'enactments': [{'node': '/test/acts/47/4',
                     'exact': 'In this Act, beard means any facial hair no shorter '
                              'than 5 millimetres in length that: occurs on or '
                              'below the chin'}],
     'universal': True}


The “universal” True/False field indicates whether the Rule is one that
applies in every case where all of the inputs are present, or only in
some cases. The default is False, but this Rule overrides that default
and says it applies in every case where all of the inputs are present.

Now we can have AuthoritySpoke read this JSON and convert it to a list
of :class:`~authorityspoke.rules.Rule` objects. In particular, we’ll look at the first two Rules, which
describe two ways that an object can be defined to be a “beard”.

    >>> beard_holdings = loaders.read_holdings_from_file("beard_rules.yaml", client=legis_client)
    >>> print(beard_holdings[0])
    the Holding to ACCEPT
      the Rule that the court MAY ALWAYS impose the
        RESULT:
          the fact that <the suspected beard> was a beard
        GIVEN:
          the fact that <the suspected beard> was facial hair
          the fact that the length of <the suspected beard> was at least 5
          millimeter
          the fact that <the suspected beard> occurred on or below the chin
        GIVEN the ENACTMENT:
          "In this Act, beard means any facial hair no shorter than 5 millimetres in length that: occurs on or below the chin…" (/test/acts/47/4 1935-04-01)


    >>> print(beard_holdings[1])
    the Holding to ACCEPT
      the Rule that the court MAY ALWAYS impose the
        RESULT:
          the fact that <the suspected beard> was a beard
        GIVEN:
          the fact that <the suspected beard> was facial hair
          the fact that the length of <the suspected beard> was at least 5
          millimeter
          the fact that <the suspected beard> existed in an uninterrupted line
          from the front of one ear to the front of the other ear below the nose
        GIVEN the ENACTMENT:
          "In this Act, beard means any facial hair no shorter than 5 millimetres in length that:…exists in an uninterrupted line from the front of one ear to the front of the other ear below the nose." (/test/acts/47/4 1935-04-01)


The difference between these two Rules is that the first one applies to
facial hair “on or below the chin” and the second applies to facial hair
“in an uninterrupted line from the front of one ear to the front of the
other ear below the nose”. I’ll rename them accordingly.

    >>> chin_rule = beard_holdings[0].rule
    >>> ear_rule = beard_holdings[1].rule

Implication and Contradiction between Rules
-------------------------------------------

AuthoritySpoke doesn’t yet have a feature that directly takes a set of
known :class:`~authorityspoke.facts.Fact`\s, applies
a :class:`~authorityspoke.rules.Rule` to them, and then infers legal conclusions.
Instead, in its current iteration, AuthoritySpoke can be used to combine
Rules together to make more Rules, or to check whether Rules imply or
contradict one another.

For instance, if we create a new Rule that’s identical to the first Rule
in the Beard Tax Act except that it applies to facial hair that’s
exactly 8 millimeters long instead of “no shorter than 5 millimetres”,
we can determine that the original “chin rule” implies our new Rule.

    >>> from authorityspoke.io import readers
    >>> beard_dictionary[0]['inputs'][1]['content'] = 'the length of the suspected beard was = 8 millimetres'
    >>> longer_hair_rule = readers.read_holding(beard_dictionary[0], client=legis_client)
    >>> print(longer_hair_rule)
    the Holding to ACCEPT
      the Rule that the court MAY ALWAYS impose the
        RESULT:
          the fact that <the suspected beard> was a beard
        GIVEN:
          the fact that <the suspected beard> was facial hair
          the fact that the length of <the suspected beard> was exactly equal to
          8 millimeter
          the fact that <the suspected beard> occurred on or below the chin
        GIVEN the ENACTMENT:
          "In this Act, beard means any facial hair no shorter than 5 millimetres in length that: occurs on or below the chin…" (/test/acts/47/4 1935-04-01)


    >>> chin_rule.implies(longer_hair_rule)
    True


Similarly, we can create a new Rule that says facial hair is *never* a
beard if its length is greater than 12 inches (we’ll use inches instead
of millimeters this time, and the units will be converted automatically
thanks to the `pint <https://pint.readthedocs.io/en/stable/>`__
library). And we can show that this new Rule contradicts a Rule that
came from the Beard Tax Act.

    >>> beard_dictionary[1]["despite"] = [
    ...     beard_dictionary[1]["inputs"][0],
    ...     beard_dictionary[1]["inputs"][2]]
    >>> beard_dictionary[1]["inputs"] = {
    ...    "type": "fact",
    ...    "content": "the length of the suspected beard was >= 12 inches"}
    >>> beard_dictionary[1]["outputs"][0]["truth"] = False
    >>> beard_dictionary[1]["mandatory"] = True
    >>> long_means_not_beard = readers.read_rule(beard_dictionary[1], client=legis_client)
    >>> print(long_means_not_beard)
    the Rule that the court MUST ALWAYS impose the
      RESULT:
        the fact it was false that <the suspected beard> was a beard
      GIVEN:
        the fact that the length of <the suspected beard> was at least 12 inch
      DESPITE:
        the fact that <the suspected beard> was facial hair
        the fact that <the suspected beard> existed in an uninterrupted line
        from the front of one ear to the front of the other ear below the nose
      GIVEN the ENACTMENT:
        "In this Act, beard means any facial hair no shorter than 5 millimetres in length that:…exists in an uninterrupted line from the front of one ear to the front of the other ear below the nose." (/test/acts/47/4 1935-04-01)



    >>> long_means_not_beard.contradicts(ear_rule)
    True



Addition between Rules
----------------------

Finally, let’s look at adding Rules. AuthoritySpoke currently only
allows Rules to be added if applying the first Rule would supply you
with all the input Factor you need to apply the second Rule as well.
Here’s an example.

The Beard Tax Act defines the offense of “improper transfer of
beardcoin”. This offense basically has three elements:

1. a transfer of beardcoin
2. the absence of a license, and
3. a counterparty who is not the Department of Beards.

But in `section
7A <https://authorityspoke.com/legislice/test/acts/47/7A@2035-08-01>`__
of the Beard Tax Act, we also learn specifically that a “loan” of the
tokens called beardcoin counts as the kind of “transfer” that will
support a conviction of the offense. We can represent this information
as a separate Rule, and then add it to the Rule defining the offense.
The result is that we discover an alternate way of establishing the
offense:

1. a loan of beardcoin
2. the absence of a license, and
3. a counterparty who is not the Department of Beards.

Here are the two Rules we’ll be adding together.

    >>> elements_of_offense = beard_holdings[11].rule
    >>> print(elements_of_offense)
    the Rule that the court MUST ALWAYS impose the
      RESULT:
        the fact that <the defendant> committed the offense of improper
        transfer of beardcoin
      GIVEN:
        the fact that <the beardcoin transaction> was a transfer of beardcoin
        between <the defendant> and <the counterparty>
        absence of the fact that <the beardcoin transaction> was a licensed
        beardcoin repurchase
        the fact it was false that <the counterparty> was <the Department of
        Beards>
      DESPITE:
        the fact that the token attributed to <the Department of Beards>,
        asserting the fact that <the Department of Beards> granted an
        exemption from the prohibition of wearing beards, was counterfeit
      GIVEN the ENACTMENTS:
        "It shall be an offence to buy, sell, lend, lease, gift, transfer or receive in any way a beardcoin from any person or body other than the Department of Beards, except as provided in Part 4." (/test/acts/47/7A 1935-04-01)
        "It shall be no defense to a charge under section 7A that the purchase, sale, lease, gift, transfer or receipt was of counterfeit beardcoin rather than genuine beardcoin." (/test/acts/47/7B/2 1935-04-01)
      DESPITE the ENACTMENT:
        "The Department of Beards may issue licenses to such barbers, hairdressers, or other male grooming professionals as they see fit to purchase a beardcoin from a customer whose beard they have removed, and to resell those beardcoins to the Department of Beards." (/test/acts/47/11 2013-07-18)


    >>> loan_is_transfer = beard_holdings[7].rule
    >>> print(loan_is_transfer)
    the Rule that the court MUST ALWAYS impose the
      RESULT:
        the fact that <the beardcoin transaction> was a transfer of beardcoin
        between <the defendant> and <the counterparty>
      GIVEN:
        the fact that <the beardcoin transaction> was <the defendant>'s loan
        of the token attributed to <the Department of Beards>, asserting the
        fact that <the Department of Beards> granted an exemption from the
        prohibition of wearing beards, to <the counterparty>
      GIVEN the ENACTMENT:
        "It shall be an offence to buy, sell, lend, lease, gift, transfer or receive in any way a beardcoin from any person or body other than the Department of Beards, except as provided in Part 4." (/test/acts/47/7A 1935-04-01)


But there’s a problem. The ``loan_is_transfer`` Rule establishes only
one of the elements of the offense. In order to create a Rule that we
can add to ``elements_of_offense``, we’ll need to add Facts establishing
the two elements other than the “transfer” element. We’ll also need to
add one of the :class:`~legislice.enactments.Enactment`\s that
the ``elements_of_offense`` :class:`~authorityspoke.rules.Rule` relies upon.

    >>> loan_without_exceptions = (
    ...             loan_is_transfer
    ...             + elements_of_offense.inputs[1]
    ...             + elements_of_offense.inputs[2]
    ...             + elements_of_offense.enactments[1]
    ...         )
    >>> print(loan_without_exceptions)
    the Rule that the court MUST ALWAYS impose the
      RESULT:
        the fact that <the beardcoin transaction> was a transfer of beardcoin
        between <the defendant> and <the counterparty>
      GIVEN:
        the fact that <the beardcoin transaction> was <the defendant>'s loan
        of the token attributed to <the Department of Beards>, asserting the
        fact that <the Department of Beards> granted an exemption from the
        prohibition of wearing beards, to <the counterparty>
        absence of the fact that <the beardcoin transaction> was a licensed
        beardcoin repurchase
        the fact it was false that <the counterparty> was <the Department of
        Beards>
      GIVEN the ENACTMENTS:
        "It shall be an offence to buy, sell, lend, lease, gift, transfer or receive in any way a beardcoin from any person or body other than the Department of Beards, except as provided in Part 4." (/test/acts/47/7A 1935-04-01)
        "It shall be no defense to a charge under section 7A that the purchase, sale, lease, gift, transfer or receipt was of counterfeit beardcoin rather than genuine beardcoin." (/test/acts/47/7B/2 1935-04-01)

With these changes, we can add together two Holdings to get a new one.

    >>> loan_is_transfer = beard_holdings[7]
    >>> elements_of_offense = beard_holdings[11]
    >>> loan_without_exceptions = (
    ...     loan_is_transfer
    ...     + elements_of_offense.inputs[1]
    ...     + elements_of_offense.inputs[2]
    ...     + elements_of_offense.enactments[1]
    ... )
    >>> loan_establishes_offense = loan_without_exceptions + elements_of_offense
    >>> print(loan_establishes_offense)
    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the fact that <the defendant> committed the offense of improper
          transfer of beardcoin
          the fact that <the beardcoin transaction> was a transfer of beardcoin
          between <the defendant> and <the counterparty>
        GIVEN:
          the fact it was false that <the counterparty> was <the Department of
          Beards>
          absence of the fact that <the beardcoin transaction> was a licensed
          beardcoin repurchase
          the fact that <the beardcoin transaction> was <the defendant>'s loan
          of the token attributed to <the Department of Beards>, asserting the
          fact that <the Department of Beards> granted an exemption from the
          prohibition of wearing beards, to <the counterparty>
        DESPITE:
          the fact that the token attributed to <the Department of Beards>,
          asserting the fact that <the Department of Beards> granted an
          exemption from the prohibition of wearing beards, was counterfeit
        GIVEN the ENACTMENTS:
          "It shall be an offence to buy, sell, lend, lease, gift, transfer or receive in any way a beardcoin from any person or body other than the Department of Beards, except as provided in Part 4." (/test/acts/47/7A 1935-04-01)
          "It shall be no defense to a charge under section 7A that the purchase, sale, lease, gift, transfer or receipt was of counterfeit beardcoin rather than genuine beardcoin." (/test/acts/47/7B/2 1935-04-01)
        DESPITE the ENACTMENT:
          "The Department of Beards may issue licenses to such barbers, hairdressers, or other male grooming professionals as they see fit to purchase a beardcoin from a customer whose beard they have removed, and to resell those beardcoins to the Department of Beards." (/test/acts/47/11 2013-07-18)

There will be additional methods for combining Rules in future versions
of AuthoritySpoke.

For now, try browsing through the beard_rules object to see how some of
the other provisions have been formalized. In all, there are 14 Rules in
the dataset.

    >>> len(beard_holdings)
    14


Future Work
-----------

The Beard Tax Act example still presents challenges that AuthoritySpoke
hasn’t yet met. Two capabilities that should be coming to AuthoritySpoke
fairly soon are the ability to model remedies like the sentencing
provisions in
`/test/acts/47/9 <https://authorityspoke.com/legislice/test/acts/47/9@1935-08-01>`__,
and commencement dates like the one in
`/test/acts/47/2 <https://authorityspoke.com/legislice/test/acts/47/2@1935-08-01>`__.

But consider how you would model these more challenging details:

The “purpose” provisions in
`/test/acts/47/3 <https://authorityspoke.com/legislice/test/acts/47/3@1935-08-01>`__
and
`/test/acts/47/10 <https://authorityspoke.com/legislice/test/acts/47/10@1935-08-01>`__

Provisions delegating regulatory power, like
`/test/acts/47/6B <https://authorityspoke.com/legislice/test/acts/47/6B@1935-08-01>`__
and
`/test/acts/47/12 <https://authorityspoke.com/legislice/test/acts/47/12@1935-08-01>`__

Provisions delegating permission to take administrative actions, like
`/test/acts/47/6/1 <https://authorityspoke.com/legislice/test/acts/47/6/1@1935-08-01>`__

Provisions delegating administrative responsibilities, like
`/test/acts/47/6D/1 <https://authorityspoke.com/legislice/test/acts/47/6D/1@1935-08-01>`__
and
`/test/acts/47/8/1 <https://authorityspoke.com/legislice/test/acts/47/8/1@1935-08-01>`__

Provisions delegating fact-finding power, like
`/test/acts/47/6D/2 <https://authorityspoke.com/legislice/test/acts/47/6D/2@1935-08-01>`__

Clauses limiting the effect of particular provisions to a certain
statutory scope, like the words “In this Act,” in
`/test/acts/47/4 <https://authorityspoke.com/legislice/test/acts/47/4@1935-08-01>`__

For more about the use of the Beard Tax Act to describe the effectiveness
of legal data modeling software, see the `Python for Law Blog. <https://pythonforlaw.com/2020/11/30/a-test-rubric-for-legal-rule-automation.html>`__

Contact
~~~~~~~

If you have questions, comments, or ideas, please feel welcome to get in
touch via Twitter at
`@AuthoritySpoke <https://twitter.com/AuthoritySpoke>`__ or
`@mcareyaus <https://twitter.com/mcareyaus>`__, or via the `AuthoritySpoke
Github repo <https://github.com/mscarey/AuthoritySpoke>`__.
