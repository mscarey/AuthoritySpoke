..  _schema_of_holdings:

Structure and Schema of AuthoritySpoke Holdings
===============================================

This tutorial will show how to create and load objects representing
legal Holdings in AuthoritySpoke.

To get ready, we need to repeat some setup steps we already saw in the
:ref:`introduction` guide. First, import the package.

    >>> import authorityspoke

Again, you have the choice of using either the real API clients or
mockups that supply only the testing data for these examples.

    >>> USE_REAL_CASE_API = False
    >>> USE_REAL_LEGISLICE_API = False

Next, we can download the judicial decisions we’re going to compare
and convert the JSON responses from the API
into :class:`authorityspoke.decisions.Decision` objects.

    >>> import os
    >>> from dotenv import load_dotenv
    >>> from authorityspoke import Decision, DecisionReading
    >>> from authorityspoke.io.loaders import load_decision_as_reading
    >>> from authorityspoke.io import CAPClient
    >>> load_dotenv(dotenv_path=".env")
    True
    >>> if USE_REAL_CASE_API:
    ...     CAP_API_KEY = os.getenv('CAP_API_KEY')
    ...     client = CAPClient(api_token=CAP_API_KEY)
    ...     oracle_decision = client.read_cite(
    ...     cite="750 F.3d 1339",
    ...     full_case=True)
    ...     lotus_decision = client.read_cite(
    ...     cite="49 F.3d 807",
    ...     full_case=True)
    ...     oracle = DecisionReading(oracle_decision)
    ...     lotus = DecisionReading(lotus_decision)
    ... else:
    ...     oracle = load_decision_as_reading("oracle_h.json")
    ...     lotus = load_decision_as_reading("lotus_h.json")


And we need a download :class:`~legislice.download.Client` for
accessing legislative provisions.

    >>> import json

    >>> from authorityspoke import LegisClient
    >>> from authorityspoke.io.fake_enactments import FakeClient
    >>> if USE_REAL_LEGISLICE_API:
    ...     LEGISLICE_API_TOKEN = os.getenv("LEGISLICE_API_TOKEN")
    ...     legis_client = LegisClient(api_token=LEGISLICE_API_TOKEN)
    ... else:
    ...     legis_client = FakeClient.from_file("usc.json")

Loading Holdings from Existing JSON
-----------------------------------

Now we’re ready to look at the process of describing a
:class:`~authorityspoke.holdings.Holding` and loading that
information into AuthoritySpoke. In
version 0.6, although there’s not yet a web interface for loading this
data, there is an interface for loading JSON files, and there’s an
OpenAPI schema specification for the input data (see below).

There are several interfaces for loading Authorityspoke objects in the
:mod:`authorityspoke.io.loaders` and :mod:`authorityspoke.io.schemas_yaml` modules.
One way to load data is to create a YAML document that
contains a list of objects, where each object represents one Holding.
Then we can load the Holdings into
AuthoritySpoke objects using
the :func:`~authorityspoke.io.loaders.read_holdings_from_file` function.

    >>> from authorityspoke.io.loaders import read_holdings_from_file

    >>> oracle_holdings = read_holdings_from_file("holding_oracle.yaml", client=legis_client)
    >>> lotus_holdings = read_holdings_from_file("holding_lotus.yaml", client=legis_client)

If we want to open one of the input YAML files in a text editor
for comparison, they can be found in the folder
``example_data/holdings/``.

``holding_oracle.yaml`` contains a list of holdings. These are places
where the text of the *Oracle* opinion endorses legal rules (or
sometimes, rejects legal rules). Each :class:`~authorityspoke.rules.Rule`
is described procedurally, in terms of inputs and outputs.

Each holding in the JSON input may also include an ``anchors`` field
indicating where the holding can be found in the opinion. For instance,
the first holding of *Oracle America v. Google* is derived from the
following sentence from the majority opinion:

   By statute, a work must be “original” to qualify for copyright
   protection. 17 U.S.C. § 102(a).

The ``anchors`` field doesn’t do much yet in AuthoritySpoke version 0.6,
but in future versions it’ll help link each Holding to the relevant
parts of the Opinion.

The Parts of a Holding as a Python Dictionary
------------------------------------------------------

Now let's look at the part of ``holding_oracle.yaml`` representing that
first holding. The :meth:`authorityspoke.io.loaders.load_holdings` method
will convert the YAML file to a Python dictionary
(with a structure similar to JSON), but won't yet load it as an
AuthoritySpoke object.

    >>> from pprint import pprint
    >>> from authorityspoke.io.loaders import load_holdings
    >>> holdings_to_read = load_holdings("holding_oracle.yaml")
    >>> pprint(holdings_to_read[0]["inputs"])
    {'content': '{the Java API} was an original work',
     'truth': False,
     'type': 'fact'}

To compare the input data to the created Python objects, link
the Holdings to the :class:`~authorityspoke.opinions.OpinionReading` using
the :meth:`~authorityspoke.opinions.OpinionReading.posit` method. As we look at
the parts of the JSON file, the code cells will show how fields from the
JSON affect the structure of the :class:`~authorityspoke.holdings.Holding`.

    >>> oracle.posit(oracle_holdings)
    >>> lotus.posit(lotus_holdings)
    >>> print(oracle.holdings[0])
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the fact it was false that <the Java API> was copyrightable
        GIVEN:
          the fact it was false that <the Java API> was an original work
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


This Holding means that according to the
cited :class:`~legislice.enactments.Enactment`, if it’s false
that “the Java API was an original work”, then it’s mandatory for the
court to find it to be false that “the Java API was copyrightable”.

The JSON file represented these :class:`~nettlesome.factors.Factor`\s
inside an “inputs” field
(labeled as the “GIVEN” Factors when you print the Holding object) and
an “outputs” field (labeled as “RESULT” Factors). Inputs are the
preconditions for applying the Holding, and outputs are the results. Not
shown here, Rules can also have “despite” Factors, which are Factors
that don’t need to be present to trigger the rule, but that don’t
prevent the rule from applying if they’re present. There can be more
than one Factor in the “inputs”, “outputs” or “despite” categories, and
if so they would be listed together in square brackets in the JSON.

    >>> print(oracle.holdings[0].inputs[0])
    the fact it was false that <the Java API> was an original work


The curly brackets around ``{the Java API}`` indicate that the parser
should consider that phrase to be a reference to an Entity object, which
becomes one of the input’s ``terms``. If such an object hasn’t
been referenced before in the file, it will be created.

    >>> print(oracle.holdings[0].inputs[0].terms)
    [Entity(generic=True, absent=False, name='the Java API', plural=False)]


The JSON representation of a Rule can also have “mandatory” and
“universal” fields. If omitted, the values of these fields are implied
as False. “universal” means that the Rule applies whenever its inputs
are present. “mandatory” means that when Rule applies, the court has no
discretion and must accept the outputs.

    >>> print(oracle.holdings[0].mandatory)
    True


The JSON can also contain fields representing Enactments. It identifies
a passage of legislative text with a `United States Legislative
Markup <https://github.com/usgpo/uslm>`__ identifier that shows the
“path” to the text. In this case, “us” refers to the jurisdiction (the
US federal government), “usc” refers to the Code (the United States
Code), “t17” specifies Title 17 of the United States Code, “s102”
specifies Section 102 of Title 17, and “a” specifies subsection (a) of
Section 102. If the relevant passage is less than the entire section or
subsection, an “exact” field can identify the full text of the passage
or “prefix” and “suffix” fields can be used to the phrase by what comes
immediately before or after it. You don’t need to include “prefix” and
“suffix” if you’re sure the phrase you’re trying to select only occurs
once in the statute subdivision you’ve cited. Alternatively, a passage
can be saved as a ``text`` field with pipe characters that split it into
three parts for “prefix”, “exact”, and “suffix” fields.

For instance, to get just the phrase “original works of authorship”, we
could have included this field in the JSON input:

.. parsed-literal::

   "text": "in accordance with this title, in|original works of authorship|fixed"

We can also :meth:`~legislice.enactments.Enactment.select` that same string
to change the :class:`~legislice.enactments.Enactment`\'s selected text
after loading the Enactment:

  >>> to_select = "in accordance with this title, in|original works of authorship|fixed"
  >>> oracle.holdings[0].enactments[0].select(to_select)

And we can use the :meth:`~legislice.enactments.BaseEnactment.selected_text`
method to verify that the Enactment's selected text has changed.

  >>> oracle.holdings[0].enactments[0].selected_text()
  '…original works of authorship…'

The “name” field is a nickname that can be used to refer to the passage
again later in the same file. For any Factor or Enactment object, you
can add a “name” field and assign a unique string value as the name. If
you need to refer to the object again in the list of Holdings you’re
importing, you can replace the object with the name string. This means a
Holding object could have “input”, “despite” and “output” fields
containing lists of string indentifiers of Factors defined elsewhere.
Enactment objects can be replaced the same way in the “enactments” and
“enactments_despite” fields.

  >>> holdings_to_read[0]["enactments"]["name"]
  'copyright protection provision'


In the second holding in the loaded dictionary representing a holding,
we can see where the enactment
is referenced by its name “copy protection provision” instead of being
repeated in its entirety.

    >>> pprint(holdings_to_read[1]["enactments"])
    ['copyright protection provision']

There can also be an “enactments_despite” field, which identifies
legislative text that doesn’t need to be present for the Rule to apply,
but that also doesn’t negate the validity of the Rule.

..  _json_api_spec:

JSON API Specification
----------------------

An OpenAPI JSON schema specification for AuthoritySpoke holdings can be
generated from a :class:`authorityspoke.holdings.Holding`\. This example
shows how to generate the schema as a Python dict and then view just the
"properties" field for the Holding model.

    >>> from authorityspoke.holdings import Holding
    >>> schema = Holding.schema()
    >>> schema["properties"]
    {'generic': {'default': False, 'title': 'Generic', 'type': 'boolean'}, 'absent': {'default': False, 'title': 'Absent', 'type': 'boolean'}, 'rule': {'$ref': '#/$defs/Rule'}, 'rule_valid': {'default': True, 'title': 'Rule Valid', 'type': 'boolean'}, 'decided': {'default': True, 'title': 'Decided', 'type': 'boolean'}, 'exclusive': {'default': False, 'title': 'Exclusive', 'type': 'boolean'}}

The schema can also be exported as JSON using
the :meth:`authorityspoke.holdings.Holding.schema_json` method.
