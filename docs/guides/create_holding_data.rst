``Creating Holding Data``
===========================================

This tutorial will show how to create and load objects representing
legal Holdings in AuthoritySpoke.

To get ready, we need to repeat some setup steps we already saw in the
``introduction`` notebook. First, import the package.

.. code:: ipython3

    import authorityspoke
    from authorityspoke.io.loaders import load_opinion

A Holding is an Opinion's interpretation of the meaning of a provision
of a legal Code.

So we need to load some Opinions.

.. code:: ipython3

    oracle = load_opinion("oracle_h.json")
    lotus = load_opinion("lotus_h.json")

And also load some legal Codes.

.. code:: ipython3

    from authorityspoke import Regime

    from authorityspoke.io.loaders import load_code

    usa = Regime()

    us_constitution = load_code("constitution.xml")
    usc_title_17 = load_code("usc17.xml")
    code_of_federal_regulations_title_37 = load_code("cfr37.xml")

    usa.set_code(us_constitution)
    usa.set_code(usc_title_17)
    usa.set_code(code_of_federal_regulations_title_37)

Now we're ready to look at the process of describing legal Holdings and
loading that information into AuthoritySpoke. In version 0.2,
AuthoritySpoke's way of creating Holding objects is to load them from
JSON files that need to be created using other tools.

.. code:: ipython3

    from authorityspoke.io.loaders import load_holdings

    oracle_holdings = load_holdings("holding_oracle.json", regime=usa)
    lotus_holdings = load_holdings("holding_lotus.json", regime=usa)

You should also open one of the input JSON files in your own text editor
for comparison. You can find them in the folder
``example_data/holdings/``.

The top level of each of these JSON files has two fields:
``"mentioned_factors"`` and ``"holdings"``. ``"mentioned_factors"``
contains a list of things that need to be mentioned more than once to
explain a Holding. Most of these have the type "Entity", which is an
object with few attributes other than "name". However,
``"mentioned_factors"`` can also include items that take their
significance from their role in litigation, like a "Fact", "Allegation",
or "Exhibit".

Here's the ``"mentioned_factors"`` field from
``example_data/holdings/holding_oracle.json``:

::

    "mentioned_factors": [

            {
                "type": "entity",
                "name": "Oracle America"
            },
            {
                "type": "entity",
                "name": "Google"
            },
            {
                "type": "entity",
                "name": "Sun Microsystems"
            },
            {
                "type": "entity",
                "name": "the Java API"
            },
            {
                "type": "entity",
                "name": "the Java language"
            }
        ]

"Oracle America" and "Google" are the names of parties to the case. But
"Sun Microsystems" is not a party, and "the Java API" and "the Java
language" are intellectual property assets the parties are fighting
over. The reason these names need to be assigned the type ``Entity`` is
that it only becomes possible to understand the Holdings of the case if
you understand that the "Google" mentioned in one Fact is the same thing
as the "Google" mentioned in another.

``holding_oracle.json`` also contains a list of holdings. These are
places where the text of the *Oracle* opinion endorses legal rules (or
sometimes, rejects legal rules). Each of these rules is described
procedurally, in terms of inputs and outputs.

Each holding in the JSON input may also include an ``anchors`` field
indicating where the holding can be found in the opinion. For instance,
the first holding of *Oracle America v. Google* is the following
sentence from the majority opinion:

    By statute, a work must be “original” to qualify for copyright
    protection. 17 U.S.C. § 102(a).

The ``anchors`` field doesn't do much yet in AuthoritySpoke version 0.2,
but in future versions it'll help link each Holding to the relevant
parts of the Opinion.

Now let's look at the part of ``holding_oracle.json`` representing that
first holding.

::

    "holdings": [{
            "inputs": {
                "type": "fact",
                "content": "the Java API was an original work",
                "truth": false
            },
            "outputs": {
                "type": "fact",
                "content": "the Java API was copyrightable",
                "truth": false
            },
            "mandatory": true,
                "enactments": {
                    "path": "/us/usc/t17/s102/a",
                    "exact": "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.",
                    "name": "copyright protection provision"
                },
                "anchors": "By statute, a work |must be “original” to qualify| for"
        },
        ...
        ]

To compare the input data to the created Python objects, you can link
the Holdings to the Opinions using the ``.posit`` method. As we look at
the parts of the JSON file, the code cells will show how fields from the
JSON affect the structure of the Holding object.

.. code:: ipython3

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
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device." (Title 17, /us/usc/t17/s102/a)


This JSON means that according to the cited enactment, if it's false
that "the Java API was an original work", then it's mandatory for the
court to find it to be false that "the Java API was copyrightable".

As you can see, Rules in AuthoritySpoke can have "inputs" (shown as
"GIVEN" Factors when you print a Rule object) and "outputs" (shown as
"RESULT" Factors). Inputs are the preconditions for applying the Rule,
and outputs are the results. Not shown here, Rules can also have
"despite" Factors, which are Factors that don't need to be present to
trigger the rule, but that don't prevent the rule from applying if
they're present. There can be more than one Factor in the "inputs",
"outputs" or "despite" categories, and if so they would be listed
together in square brackets in the JSON.

.. code:: ipython3

    print(oracle.holdings[0].inputs[0])


.. parsed-literal::

    the Fact it is false that <the Java API> was an original work


The JSON representation of a Rule can also have "mandatory" and
"universal" fields. If omitted, the values of these fields are implied
as False. "universal" means that the Rule applies whenever its inputs
are present. "mandatory" means that when Rule applies, the court has no
discretion and must accept the outputs.

.. code:: ipython3

    print(oracle.holdings[0].mandatory)


.. parsed-literal::

    True


The JSON can also contain fields representing Enactments. It identifies
a passage of legislative text with a `United States Legislative
Markup <https://github.com/usgpo/uslm>`__ identifier that shows the
"path" to the text. In this case, "us" refers to the jurisdiction (the
US federal government), "usc" refers to the Code (the United States
Code), "t17" specifies Title 17 of the United States Code, "s102"
specifies Section 102 of Title 17, and "a" specifies subsection (a) of
Section 102. If the relevant passage is less than the entire section or
subsection, an "exact" field can identify the full text of the passage
or "prefix" and "suffix" fields can be used to the phrase by what comes
immediately before or after it. Alternatively, a passage can be saved as
a ``text`` field with pipe characters that split it into three parts for
"prefix", "exact", and "suffix" fields. You don't need to include
"prefix" and "suffix" if you're sure the phrase you're trying to select
only occurs once in the statute subdivision you've cited.

For instance, to get just the phrase "original works of authorship", we
could have used the field:

::

    "text": "in accordance with this title, in|original works of authorship|fixed"

.. code:: ipython3

    print(oracle.holdings[0].enactments[0])


.. parsed-literal::

    "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device." (Title 17, /us/usc/t17/s102/a)


The text selector in the example had just an ``exact`` field, with no
``prefix`` or ``suffix``.

.. code:: ipython3

    print(oracle.holdings[0].enactments[0].selector.prefix)


.. parsed-literal::

    None


The "name" field is simply a nickname that can be used to refer to the
passage again later in the same file.

.. code:: ipython3

    print(oracle.holdings[0].enactments[0].name)


.. parsed-literal::

    copyright protection provision


There can also be an "enactments\_despite" field, which identifies
legislative text that doesn't need to be present for the Rule to apply,
but that also doesn't negate the validity of the Rule.

Unfortunately, there's not yet a formal JSON schema for this input, and
the interface is still in flux. Keep an eye on `AuthoritySpoke's GitHub
repo <https://github.com/mscarey/AuthoritySpoke>`__ for progress or, if
you have ideas to move this feature forward, post on the `issues
page <https://github.com/mscarey/AuthoritySpoke/issues>`__.
