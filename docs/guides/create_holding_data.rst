..  _create_holding_data:

``Creating Holding Data``
======================================

This tutorial will show how to create and load objects representing
legal :class:`.Holding`\s in AuthoritySpoke.

To get ready, we need to repeat some setup steps we already saw in the
``introduction`` notebook. First, import the package.

.. code:: python

    import authorityspoke
    from authorityspoke.io.loaders import load_and_read_decision

A Holding is an :class:`.Opinion`\’s interpretation of the meaning of a
provision of a legal :class:`.Code`\.

So we need to load some Opinions.

.. code:: python

    oracle = load_and_read_decision("oracle_h.json").majority
    lotus = load_and_read_decision("lotus_h.json").majority

And also load some legal Codes.

.. code:: python

    from authorityspoke import Regime

    from authorityspoke.io.loaders import load_and_read_code

    usa = Regime()

    us_constitution = load_and_read_code("constitution.xml")
    usc_title_17 = load_and_read_code("usc17.xml")
    code_of_federal_regulations_title_37 = load_and_read_code("cfr37.xml")

    usa.set_code(us_constitution)
    usa.set_code(usc_title_17)
    usa.set_code(code_of_federal_regulations_title_37)

Loading Holdings from Existing JSON
-----------------------------------

Now we’re ready to look at the process of describing legal Holdings and
loading that information into AuthoritySpoke. In version 0.3, although
there’s not yet a web interface for loading this data, there is an
interface for loading JSON files, and there’s an OpenAPI schema
specification for the input data (see below).

Although there are several interfaces for loading Authorityspoke objects
in the ``authorityspoke.io.loaders`` and ``authorityspoke.io.schemas``
modules, the most useful way to load data is to create a JSON document
that contains a list of objects, where each object represents one
Holding representing a list of Holdings. Then you can load the Holdings
into AuthoritySpoke objects using the
:func:`.loaders.load_and_read_holdings` function.

.. code:: python

    from authorityspoke.io.loaders import load_and_read_holdings

    oracle_holdings = load_and_read_holdings("holding_oracle.json", regime=usa)
    lotus_holdings = load_and_read_holdings("holding_lotus.json", regime=usa)

If you want to open one of the input JSON files in your own text editor
for comparison, you can find them in the folder
``example_data/holdings/``.

``holding_oracle.json`` contains a list of holdings. These are places
where the text of the *Oracle* opinion endorses legal rules (or
sometimes, rejects legal rules). Each of these rules is described
procedurally, in terms of inputs and outputs.

Each holding in the JSON input may also include an ``anchors`` field
indicating where the holding can be found in the opinion. For instance,
the first holding of *Oracle America v. Google* is derived from the
following sentence from the majority opinion:

   By statute, a work must be “original” to qualify for copyright
   protection. 17 U.S.C. § 102(a).

The ``anchors`` field doesn’t do much yet in AuthoritySpoke version 0.3,
but in future versions it’ll help link each Holding to the relevant
parts of the Opinion.

The Parts of a Holding in JSON
-----------------------------------

Now let’s look at the part of ``holding_oracle.json`` representing that
first holding.

::

   "holdings": [
       {
           "inputs": {
               "type": "fact",
               "content": "{the Java API} was an original work",
               "truth": false,
               "anchors": "a work must be “original”"
           },
           "outputs": {
               "type": "fact",
               "content": "the Java API was copyrightable",
               "truth": false,
               "anchors": "must be “original” to qualify for |copyright protection.|"
           },
           "mandatory": true,
           "enactments": {
               "node": "/us/usc/t17/s102/a",
               "exact": "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.",
               "name": "copyright protection provision",
               "anchors": "qualify for copyright protection. |17 U.S.C. § 102(a)|."
           },
           "anchors": "By statute, a work |must be “original” to qualify| for"
       },
       ]

To compare the input data to the created Python objects, you can link
the Holdings to the Opinions using the :meth:`~.Opinion.posit` method. As we look at
the parts of the JSON file, the code cells will show how fields from the
JSON affect the structure of the Holding object.

.. code:: python

    oracle.posit(oracle_holdings)
    lotus.posit(lotus_holdings)

    print(oracle.holdings[0])


.. parsed-literal::

    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <the Java API> was copyrightable
        GIVEN:
          the Fact it is false that <the Java API> was an original work
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in
          original works of authorship fixed in any tangible medium of
          expression, now known or later developed, from which they can be
          perceived, reproduced, or otherwise communicated, either directly or
          with the aid of a machine or device." (Title 17, /us/usc/t17/s102/a)


This Holding means that according to the cited enactment, if it’s false
that “the Java API was an original work”, then it’s mandatory for the
court to find it to be false that “the Java API was copyrightable”.

The JSON file represented these Factors inside an “inputs” field
(labeled as the “GIVEN” Factors when you print the Holding object) and
an “outputs” field (labeled as “RESULT” Factors). Inputs are the
preconditions for applying the Holding, and outputs are the results. Not
shown here, Rules can also have “despite” Factors, which are Factors
that don’t need to be present to trigger the rule, but that don’t
prevent the rule from applying if they’re present. There can be more
than one Factor in the “inputs”, “outputs” or “despite” categories, and
if so they would be listed together in square brackets in the JSON.

.. code:: python

    print(oracle.holdings[0].inputs[0])


.. parsed-literal::

    the Fact it is false that <the Java API> was an original work


The curly brackets around ``{the Java API}`` indicate that the parser
should consider that phrase to be a reference to an Entity object, which
becomes one of the input’s :meth:`~.Factor.context_factors`\.
If such an object hasn’t been referenced before in the file,
it will be created.

.. code:: python

    print(oracle.holdings[0].inputs[0].context_factors)


.. parsed-literal::

    (Entity(name='the Java API', generic=True, plural=False),)


The JSON representation of a Rule can also have “mandatory” and
“universal” fields. If omitted, the values of these fields are implied
as False. “universal” means that the Rule applies whenever its inputs
are present. “mandatory” means that when Rule applies, the court has no
discretion and must accept the outputs.

.. code:: python

    print(oracle.holdings[0].mandatory)


.. parsed-literal::

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
could have used the field:

::

   "text": "in accordance with this title, in|original works of authorship|fixed"

.. code:: python

    print(oracle.holdings[0].enactments[0])


.. parsed-literal::

    "Copyright protection subsists, in accordance with this title, in
    original works of authorship fixed in any tangible medium of
    expression, now known or later developed, from which they can be
    perceived, reproduced, or otherwise communicated, either directly or
    with the aid of a machine or device." (Title 17, /us/usc/t17/s102/a)


The text selector in the example had just an ``exact`` field, with no
``prefix`` or ``suffix``.

.. code:: python

    oracle.holdings[0].enactments[0].selector.prefix




.. parsed-literal::

    ''



The “name” field is a nickname that can be used to refer to the passage
again later in the same file. For any Factor or Enactment object, you
can add a “name” field and assign a unique string value as the name. If
you need to refer to the object again in the list of Holdings you’re
importing, you can replace the object with the name string. This means a
Holding object could have “input”, “despite” and “output” fields
containing lists of string indentifiers of Factors defined elsewhere.
Enactment objects can be replaced the same way in the “enactments” and
“enactments_despite” fields.

.. code:: python

    print(oracle.holdings[0].enactments[0].name)


.. parsed-literal::

    copyright protection provision


In the second holding in the JSON file, you can see where the enactment
is referenced by its name “copy protection provision” instead of being
repeated in its entirety.

::

       {
           "inputs": [
               {
                   "type": "fact",
                   "content": "the Java API was independently created by the author, as opposed to copied from other works",
                   "anchors": "the work was independently created by the author (as opposed to copied from other works)"
               },
               {
                   "type": "fact",
                   "content": "the Java API possessed at least some minimal degree of creativity",
                   "anchors": "it possesses at least some minimal degree of creativity."
               }
           ],
           "outputs": {
               "type": "fact",
               "content": "the Java API was an original work",
               "anchors": "Original, as the term is used in copyright"
           },
           "mandatory": true,
           "universal": true,
           "enactments": "copyright protection provision"
       },

There can also be an “enactments_despite” field, which identifies
legislative text that doesn’t need to be present for the Rule to apply,
but that also doesn’t negate the validity of the Rule.

JSON API Specification
-----------------------------------

If you want to view the schema specification, you can view it by
calling :func:`.io.api_spec.make_spec`\. When you read it,
you might be surprised to see that every Holding object contains a Rule,
and every :class:`.Rule` contains a :class:`.Procedure`\.

If you prefer, instead of nesting a Rule object and Procedure object
inside the Holding object, AuthoritySpoke’s data loading library allows
you to place all the properties of the Rule and the Procedure directly
into the Holding object, as shown in the examples above.

.. code:: python

    from authorityspoke.io.api_spec import make_spec

    yaml = make_spec().to_yaml()

    # Viewing the schema specification used for AuthoritySpoke's schema objects in the YAML format
    print(yaml)


.. parsed-literal::

    components:
      schemas:
        Allegation:
          properties:
            absent:
              default: false
              type: boolean
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
            name:
              default: null
              nullable: true
              type: string
            selector:
              allOf:
              - $ref: '#/components/schemas/Selector'
              default: null
              nullable: true
            source:
              format: url
              type: string
          type: object
        Entity:
          properties:
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
            stated_by:
              allOf:
              - $ref: '#/components/schemas/Entity'
              default: null
              nullable: true
            statement:
              allOf:
              - $ref: '#/components/schemas/Fact'
              default: null
              nullable: true
          type: object
        Fact:
          properties:
            absent:
              default: false
              type: boolean
            context_factors:
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
            reciprocal:
              default: false
              type: boolean
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
            exact:
              default: ''
              type: string
            prefix:
              default: ''
              type: string
            suffix:
              default: ''
              type: string
          type: object
    info:
      description: An interface for annotating judicial holdings
      title: AuthoritySpoke Holding API
      version: 0.1.0
    openapi: 3.0.2
    paths: {}

Exporting AuthoritySpoke Holdings back to JSON
----------------------------------------------

Finally, if you want to convert an AuthoritySpoke object back to JSON or
to a Python dictionary, you can do so with :func:`.io.dump.to_json` or
:func:`.io.dump.to_dict`\. If you need to make some changes to an
AuthoritySpoke object, one way to do
so would be to convert it to JSON, edit the JSON, and then load it back
into AuthoritySpoke. The JSON format is also easier to store and share
over the web.

.. code:: python

    from authorityspoke.io import dump

    dump.to_dict(oracle.holdings[0])


.. parsed-literal::

    {'exclusive': False,
     'rule': {'procedure': {'inputs': [{'absent': False,
         'name': 'false the Java API was an original work',
         'context_factors': [{'name': 'the Java API',
           'generic': True,
           'plural': False,
           'type': 'Entity'}],
         'predicate': {'truth': False,
          'reciprocal': False,
          'content': '{} was an original work',
          'quantity': None,
          'comparison': ''},
         'generic': False,
         'standard_of_proof': None,
         'type': 'Fact'}],
       'despite': [],
       'outputs': [{'absent': False,
         'name': 'false the Java API was copyrightable',
         'context_factors': [{'name': 'the Java API',
           'generic': True,
           'plural': False,
           'type': 'Entity'}],
         'predicate': {'truth': False,
          'reciprocal': False,
          'content': '{} was copyrightable',
          'quantity': None,
          'comparison': ''},
         'generic': False,
         'standard_of_proof': None,
         'type': 'Fact'}]},
      'name': None,
      'enactments': [{'name': 'copyright protection provision',
        'selector': {'prefix': '',
         'suffix': '',
         'exact': 'Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.'},
        'source': '/us/usc/t17/s102/a'}],
      'mandatory': True,
      'universal': False,
      'generic': False,
      'enactments_despite': []},
     'decided': True,
     'generic': False,
     'rule_valid': True}



