..  _create_holding_data:

Creating Holding Data for AuthoritySpoke
========================================

This tutorial will show how to create and load objects representing
legal Holdings in AuthoritySpoke.

To get ready, we need to repeat some setup steps we already saw in the
:ref:`introduction` guide. First, import the package.

.. code:: ipython3

    import authorityspoke
    from authorityspoke.io.downloads import download_case
    from authorityspoke.io.loaders import load_decision

Again, you have the choice of using either the real API clients or
mockups that supply only the testing data for these examples.

.. code:: ipython3

    USE_REAL_CASE_API = True
    USE_REAL_LEGISLICE_API = True

Next, we can download the judicial decisions we’re going to compare.

.. code:: ipython3

    import os
    from dotenv import load_dotenv
    load_dotenv()

    if USE_REAL_CASE_API:
        CAP_API_KEY = os.getenv('CAP_API_KEY')

        oracle_download = download_case(
        cite="750 F.3d 1339",
        full_case=True,
        api_key=CAP_API_KEY)

        lotus_download = download_case(
        cite="49 F.3d 807",
        full_case=True,
        api_key=CAP_API_KEY)

    else:
        oracle_download = load_decision("oracle_h.json")
        lotus_download = load_decision("lotus_h.json")

Then we convert the JSON responses from the API into AuthoritySpoke
``Opinion`` objects.

.. code:: ipython3

    from authorityspoke.io.readers import read_decision

    oracle = read_decision(oracle_download).majority
    lotus = read_decision(lotus_download).majority

And we need a :class:`~authorityspoke.io.downloads.Client` for
accessing legislative provisions.

.. code:: ipython3

    import json

    from authorityspoke.io.downloads import Client
    from authorityspoke.io.fake_clients import FakeClient

    if USE_REAL_LEGISLICE_API:

        LEGISLICE_API_TOKEN = os.getenv("LEGISLICE_API_TOKEN")
        legis_client = Client(api_token=LEGISLICE_API_TOKEN)

    else:
        legis_client = FakeClient.from_file("usc.json")

Loading Holdings from Existing JSON
-----------------------------------

Now we’re ready to look at the process of describing a
:class:`~authorityspoke.holdings.Holding` and loading that
information into AuthoritySpoke. In
version 0.4, although there’s not yet a web interface for loading this
data, there is an interface for loading JSON files, and there’s an
OpenAPI schema specification for the input data (see below).

Although there are interfaces for loading Authorityspoke objects in the
:mod:`authorityspoke.io.loaders` and :mod:`authorityspoke.io.schemas` modules,
the most useful way to load data is to create a JSON document that
contains a list of objects, where each object represents one Holding
representing a list of Holdings. Then you can load the Holdings into
AuthoritySpoke objects using
the :func:`~authorityspoke.io.loaders.load_and_read_holdings` function.

.. code:: ipython3

    from authorityspoke.io.loaders import load_and_read_holdings

    oracle_holdings = load_and_read_holdings("holding_oracle.json", client=legis_client)
    lotus_holdings = load_and_read_holdings("holding_lotus.json", client=legis_client)

If you want to open one of the input JSON files in your own text editor
for comparison, you can find them in the folder
``example_data/holdings/``.

``holding_oracle.json`` contains a list of holdings. These are places
where the text of the *Oracle* opinion endorses legal rules (or
sometimes, rejects legal rules). Each :class:`~authorityspoke.rules.Rule`
is described procedurally, in terms of inputs and outputs.

Each holding in the JSON input may also include an ``anchors`` field
indicating where the holding can be found in the opinion. For instance,
the first holding of *Oracle America v. Google* is derived from the
following sentence from the majority opinion:

   By statute, a work must be “original” to qualify for copyright
   protection. 17 U.S.C. § 102(a).

The ``anchors`` field doesn’t do much yet in AuthoritySpoke version 0.4,
but in future versions it’ll help link each Holding to the relevant
parts of the Opinion.

The Parts of a Holding in JSON
------------------------------

Now let’s look at the part of ``holding_oracle.json`` representing that
first holding.

    >>> from authorityspoke.io.loaders import load_holdings
    >>> holdings_to_read = load_holdings("holding_oracle.json")
    >>> holdings_to_read[0]
    {'inputs': {'type': 'fact',
      'content': '{the Java API} was an original work',
      'truth': False,
      'anchors': 'a work must be “original”'},
     'outputs': {'type': 'fact',
      'content': 'the Java API was copyrightable',
      'truth': False,
      'anchors': 'must be “original” to qualify for ``|copyright protection.|``'},
     'mandatory': True,
     'enactments': {'node': '/us/usc/t17/s102/a',
      'exact': 'Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.',
      'name': 'copyright protection provision',
      'anchors': 'qualify for copyright protection. ``|17 U.S.C. § 102(a)|``.'},
     'anchors': 'By statute, a work ``|must be “original” to qualify|`` for'}



To compare the input data to the created Python objects, you can link
the Holdings to the :class:`~authorityspoke.opinions.Opinion` using
the :meth:`~authorityspoke.opinions.Opinion.posit` method. As we look at
the parts of the JSON file, the code cells will show how fields from the
JSON affect the structure of the :class:`~authorityspoke.holdings.Holding` object.

    >>> oracle.posit(oracle_holdings)
    >>> lotus.posit(lotus_holdings)
    >>> print(oracle.holdings[0])
    "the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <the Java API> was copyrightable
        GIVEN:
          the Fact it is false that <the Java API> was an original work
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)"


This Holding means that according to the
cited :class:`~legislice.enactments.Enactment`, if it’s false
that “the Java API was an original work”, then it’s mandatory for the
court to find it to be false that “the Java API was copyrightable”.

The JSON file represented these :class:`~authorityspoke.factors.Factor`\s
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
    "the Fact it is false that <the Java API> was an original work"


The curly brackets around ``{the Java API}`` indicate that the parser
should consider that phrase to be a reference to an Entity object, which
becomes one of the input’s ``terms``. If such an object hasn’t
been referenced before in the file, it will be created.

    >>> print(oracle.holdings[0].inputs[0].terms)
    (Entity(name='the Java API', generic=True, plural=False, anchors=[]),)


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


In the second holding in the JSON file, you can see where the enactment
is referenced by its name “copy protection provision” instead of being
repeated in its entirety.

    >>> holdings_to_read[1]
    {'inputs': [{'type': 'fact',
       'content': 'the Java API was independently created by the author, as opposed to copied from other works',
       'anchors': 'the work was independently created by the author (as opposed to copied from other works)'},
      {'type': 'fact',
       'content': 'the Java API possessed at least some minimal degree of creativity',
       'anchors': 'it possesses at least some minimal degree of creativity.'}],
     'outputs': {'type': 'fact',
      'content': 'the Java API was an original work',
      'anchors': 'Original, as the term is used in copyright'},
     'mandatory': True,
     'universal': True,
     'enactments': 'copyright protection provision'}



There can also be an “enactments_despite” field, which identifies
legislative text that doesn’t need to be present for the Rule to apply,
but that also doesn’t negate the validity of the Rule.

..  _json_api_spec:

JSON API Specification
----------------------

If you want to view the schema specification, you can find it in the
``io.api_spec`` module. When you read it, you might be surprised to see
that every Holding object contains a Rule, and every Rule contains a
Procedure.

If you prefer, instead of nesting a Rule object and Procedure object
inside the Holding object, AuthoritySpoke’s data loading library allows
you to place all the properties of the Rule and the Procedure directly
into the Holding object, as shown in the examples above.

    >>> from authorityspoke.io.api_spec import make_spec
    >>> yaml = make_spec().to_yaml()
    >>> print(yaml)


.. parsed-literal::

    components:
      schemas:
        Allegation:
          properties:
            absent:
              default: false
              type: boolean
            anchors:
              items:
                $ref: '#/components/schemas/Selector'
              type: array
            generic:
              default: false
              type: boolean
            name:
              default: null
              nullable: true
              type: string
            pleading:
              allOf:
              - $ref: '#/components/schemas/Pleading'
              default: null
              nullable: true
            statement:
              allOf:
              - $ref: '#/components/schemas/Fact'
              default: null
              nullable: true
          type: object
        Enactment:
          properties:
            anchors:
              items:
                $ref: '#/components/schemas/Selector'
              type: array
            children:
              items:
                $ref: '#/components/schemas/Enactment'
              type: array
            content:
              type: string
            end_date:
              default: null
              format: date
              nullable: true
              type: string
            heading:
              type: string
            node:
              format: url
              type: string
            selection:
              items:
                $ref: '#/components/schemas/Selector'
              type: array
            start_date:
              format: date
              type: string
          required:
          - content
          - heading
          - node
          - start_date
          type: object
        Entity:
          properties:
            anchors:
              items:
                $ref: '#/components/schemas/Selector'
              type: array
            generic:
              default: true
              type: boolean
            name:
              default: null
              nullable: true
              type: string
            plural:
              type: boolean
          type: object
        Evidence:
          properties:
            absent:
              default: false
              type: boolean
            anchors:
              items:
                $ref: '#/components/schemas/Selector'
              type: array
            exhibit:
              allOf:
              - $ref: '#/components/schemas/Exhibit'
              default: null
              nullable: true
            generic:
              default: false
              type: boolean
            name:
              default: null
              nullable: true
              type: string
            to_effect:
              allOf:
              - $ref: '#/components/schemas/Fact'
              default: null
              nullable: true
          type: object
        Exhibit:
          properties:
            absent:
              default: false
              type: boolean
            anchors:
              items:
                $ref: '#/components/schemas/Selector'
              type: array
            form:
              default: null
              nullable: true
              type: string
            generic:
              default: false
              type: boolean
            name:
              default: null
              nullable: true
              type: string
            statement:
              allOf:
              - $ref: '#/components/schemas/Fact'
              default: null
              nullable: true
            statement_attribution:
              allOf:
              - $ref: '#/components/schemas/Entity'
              default: null
              nullable: true
          type: object
        Fact:
          properties:
            absent:
              default: false
              type: boolean
            anchors:
              items:
                $ref: '#/components/schemas/Selector'
              type: array
            terms:
              items:
                $ref: '#/components/schemas/Factor'
              type: array
            generic:
              default: false
              type: boolean
            name:
              default: null
              nullable: true
              type: string
            predicate:
              $ref: '#/components/schemas/Predicate'
            standard_of_proof:
              default: null
              nullable: true
              type: string
          type: object
        Factor:
          discriminator:
            propertyName: type
          oneOf:
          - $ref: '#/components/schemas/Fact'
          - $ref: '#/components/schemas/Exhibit'
          - $ref: '#/components/schemas/Evidence'
          - $ref: '#/components/schemas/Pleading'
          - $ref: '#/components/schemas/Allegation'
        Holding:
          properties:
            anchors:
              items:
                $ref: '#/components/schemas/Selector'
              type: array
            decided:
              default: true
              type: boolean
            exclusive:
              default: false
              type: boolean
            generic:
              default: false
              type: boolean
            rule:
              $ref: '#/components/schemas/Rule'
            rule_valid:
              default: true
              type: boolean
          type: object
        Pleading:
          properties:
            absent:
              default: false
              type: boolean
            anchors:
              items:
                $ref: '#/components/schemas/Selector'
              type: array
            filer:
              allOf:
              - $ref: '#/components/schemas/Entity'
              default: null
              nullable: true
            generic:
              default: false
              type: boolean
            name:
              default: null
              nullable: true
              type: string
          type: object
        Predicate:
          properties:
            comparison:
              default: ''
              enum:
              - ''
              - '>='
              - ==
              - <>
              - <=
              - '='
              - '>'
              - <
              type: string
            content:
              type: string
            quantity:
              default: null
              nullable: true
            truth:
              default: true
              type: boolean
          type: object
        Procedure:
          properties:
            despite:
              items:
                $ref: '#/components/schemas/Factor'
              type: array
            inputs:
              items:
                $ref: '#/components/schemas/Factor'
              type: array
            outputs:
              items:
                $ref: '#/components/schemas/Factor'
              type: array
          type: object
        Rule:
          properties:
            enactments:
              items:
                $ref: '#/components/schemas/Enactment'
              type: array
            enactments_despite:
              items:
                $ref: '#/components/schemas/Enactment'
              type: array
            generic:
              default: false
              type: boolean
            mandatory:
              default: false
              type: boolean
            name:
              default: null
              nullable: true
              type: string
            procedure:
              $ref: '#/components/schemas/Procedure'
            universal:
              default: false
              type: boolean
          type: object
        Selector:
          properties:
            end:
              format: int32
              type: integer
            exact:
              default: null
              nullable: true
              type: string
            include_end:
              default: false
              type: boolean
            include_start:
              default: true
              type: boolean
            prefix:
              default: null
              nullable: true
              type: string
            start:
              format: int32
              type: integer
            suffix:
              default: null
              nullable: true
              type: string
          type: object
    info:
      description: An interface for annotating judicial holdings
      title: AuthoritySpoke Holding API Schema
      version: 0.1.0
    openapi: 3.0.2
    paths: {}


Exporting AuthoritySpoke Holdings back to JSON
----------------------------------------------

Finally, if you want to convert an AuthoritySpoke object back to JSON or
to a Python dictionary, you can do so with the :mod:`~authorityspoke.io.dump` module.
Although no API exists yet for serving and ingesting data using the
AuthoritySpoke Holding Schema, this JSON format is easier to store and
share over the web.

    >>> from authorityspoke.io import dump
    >>> dump.to_json(oracle.holdings[0].outputs[0])
    '{"name": "false the Java API was copyrightable", "standard_of_proof": null, "terms": [{"name": "the Java API", "plural": false, "anchors": [], "generic": true, "type": "Entity"}], "predicate": {"expression": null, "truth": false, "sign": "", "content": "{} was copyrightable"}, "generic": false, "absent": false, "anchors": [{"exact": "copyright protection.", "prefix": "must be \\u201coriginal\\u201d to qualify for ", "suffix": ""}, {"exact": "whether the non-literal elements of a program \\u201care protected", "prefix": "", "suffix": ""}]}'
