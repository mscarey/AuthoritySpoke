..  _create_holding_data:

Creating and Loading Holding Data
=================================

This tutorial will show how to load objects representing judicial
holdings into AuthoritySpoke. First we'll see how to create an instance
of the :class:`~authorityspoke.holdings.Holding` class using Python
commands in a Python shell or notebook. Then we'll create a second
holding in a separate text file in
the YAML format, and we'll load that YAML file into AuthoritySpoke.
We'll see that when AuthoritySpoke loads holdings from YAML, those
holdings can be written in a more succinct format with more
abbreviations. Then we'll demonstrate that the two Holdings we created
can be used together even though they were created with different
techniques.

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

    >>> import os
    >>> from dotenv import load_dotenv
    >>> load_dotenv()
    >>> CAP_API_KEY = os.getenv('CAP_API_KEY')

Next, we'll create a :class:`~authorityspoke.io.downloads.CAPClient` object,
which is a download client for
getting decisions from the Caselaw Access Project. It has methods to
:meth:`~authorityspoke.io.downloads.CAPClient.fetch` decisions,
which means to get them in standard JSON format, and
also methods to :meth:`~authorityspoke.io.downloads.CAPClient.read`
decisions, which means to fetch them and then
convert them into AuthoritySpoke Decision objects. Since we know the
citation of the case we want, we'll use the ``read_cite`` method.

.. code:: ipython3

    from authorityspoke.io.downloads import CAPClient

    client = CAPClient(api_token=CAP_API_KEY)

    licensing_case = client.read_cite(
        cite="621 F.3d 205",
        full_case=True)

    print(licensing_case)


.. parsed-literal::

    United States v. Mazza-Alaluf, 621 F.3d 205 (2010-09-22)


Creating Holdings with Python
-----------------------------

Now we'll try creating a Holding from the Mazza-Alaluf case using Python
commands. One main idea from this case is that certain violations of
state law can establish an element of a federal criminal offense called
"conducting a money transmitting business without a license required by
state law". To model this concept in AuthoritySpoke we need to make it
procedural. In the context of a litigation process, the Holding tells us
something about how one factual finding can lead to another.

.. code:: ipython3

    from authorityspoke import Entity, Fact, Holding

    new_york_offense = Fact(
        "$defendant used ${defendant}'s business $business to commit the New York offense "
        "of engaging in the business of receiving money "
        "for transmission or transmitting the same, without a license therefor",
        terms=[Entity("Mazza-Alaluf"), Entity("Turismo Costa Brava")])

    no_appropriate_state_license = Fact(
        ("$defendant operated $business without an appropriate money transmitting "
        "license in a State where such operation was punishable as a misdemeanor "
        "or a felony under State law"),
        terms=[Entity("Mazza-Alaluf"), Entity("Turismo Costa Brava")])

    new_york_holding = Holding.from_factors(
        inputs=new_york_offense,
        outputs=no_appropriate_state_license,
        universal=True)

    print(new_york_holding)


.. parsed-literal::

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
Legislice API, so we're going to need a second API client class, called
LegisClient. While ``CAPClient`` was for getting court opinions,
``LegisClient`` is for getting legislation. Once again we need to `sign
up for an API token <https://authorityspoke.com/account/signup/>`__,
then save that API token in the ``.env`` file, and then load the API
token using ``dotenv``.

.. code:: ipython3

    from authorityspoke.io.downloads import LegisClient
    LEGISLICE_API_TOKEN = os.getenv("LEGISLICE_API_TOKEN")
    LEGIS_CLIENT = LegisClient(api_token=LEGISLICE_API_TOKEN)

Now we can use the ``LegisClient`` to download statutes from the United
States Code. We do this by specifying a URL-like path to the statute we
want. (These path identifiers are also used by the US government's
United States Legislative Markup format.) Here, we want part of
United States Code title 18, section 1960(b)(1). The path to that
provision is "/us/usc/t18/s1960/b/1".

.. code:: ipython3

    definition_statute = LEGIS_CLIENT.read("/us/usc/t18/s1960/b/1")
    print(definition_statute)


.. parsed-literal::

    "the term “unlicensed money transmitting business” means a money transmitting business which affects interstate or foreign commerce in any manner or degree and— is operated without an appropriate money transmitting license in a State where such operation is punishable as a misdemeanor or a felony under State law, whether or not the defendant knew that the operation was required to be licensed or that the operation was so punishable; fails to comply with the money transmitting business registration requirements under section 5330 of title 31, United States Code, or regulations prescribed under such section; or otherwise involves the transportation or transmission of funds that are known to the defendant to have been derived from a criminal offense or are intended to be used to promote or support unlawful activity;" (/us/usc/t18/s1960/b/1 2013-07-18)


We don't have to use the entire text of this statute provision. Instead
we can ``select`` just the part of the text we want. Using the ``end``
parameter, we can indicate that we want everything through the string
we've identified as the ``end``, but that we don't want anything past
that.

.. code:: ipython3

    definition_statute.select(end="or a felony under State law")

One way to add this Enactment to the Holding is by using the addition
operator (the plus sign).

.. code:: ipython3

    holding_from_python = new_york_holding + definition_statute
    print(holding_from_python)


.. parsed-literal::

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
But there's a problem: Python is a programming language, not a data
storage format (unless we wanted to store our data in Python's
`pickle <https://docs.python.org/3/library/pickle.html>`__ format, which
is usually not the best choice). We want a way to store data about legal
doctrines without writing Python commands or running a Python
interpreter. So in the next section, we'll try creating a second holding
in YAML, a structured data format based on readable text files.

..  _create_holdings_as_yaml_data:

Creating Holdings as YAML Data
------------------------------

AuthoritySpoke's YAML data import workflow is designed for creating
summaries of Holdings by hand, and then loading them into AuthoritySpoke
to convert them into computable Python objects. Under the hood, the data
import script will first convert the YAML file into JSON, and then it
will load the data into AuthoritySpoke using a JSON schema. If you're
not creating data by hand (for instance, if you're passing JSON data
from a web API into AuthoritySpoke or vice versa) then you probably will
be working with JSON directly and you won't need to use the YAML data
format.

Similar to JSON, a YAML file can be converted into a structure of nested
Python dictionaries and Python lists. A YAML file that AuthoritySpoke
can understand should start with ``holdings:`` on a line by itself
followed by an indented list of summaries of holdings. YAML uses
whitespace and hyphens to represent the structure of the data fields in
the file.

The ``holdings`` Field
~~~~~~~~~~~~~~~~~~~~~~

In YAML, a list is indicated by putting a hyphen before every item of
the list. The ``holdings`` field should contain a list of Holdings, but
each Holding itself has multiple fields. Inserting a hyphen before one
of those fields indicates where one Holding ends and the next begins.
For instance, the YAML file would have this structure if it contained
two Holdings, and each Holding had fields named "inputs", "outputs", and
"enactments".

::

    holdings:
      - inputs:
        outputs:
        enactments:
      - inputs:
        outputs:
        enactments:

To be brief, we'll start with an example YAML file that only contains one
Holding.

Factors and Entities in AuthoritySpoke YAML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The fields ``inputs``, ``outputs``, and ``despite`` should each contain
a list of ``Factors``. (If any of them is an empty list with no Factors,
then it can be omitted.) A Factor can be any of several ``type``\ s,
including ``Fact``, ``Evidence``, ``Exhibit``, ``Pleading``, or
``Allegation``. Let's add one ``Factor`` to the ``inputs`` field of the
first Holding.

::

    holdings:
      - inputs:
          - type: fact
            content: "{Mazza-Alaluf} operated {Turismo Costa Brava} without an appropriate money transmitting license in a State where such operation was punishable as a misdemeanor or a felony under State law"
            anchors: we conclude that sufficient evidence supports Mazza-Alaluf's convictions under 18 U.S.C. § 1960(b)(1)(A) for conspiring to operate and operating a money transmitting business without appropriate state licenses.

So this Factor has "type" Fact, it has some content, and it has an
"anchors" field. The purpose of the "anchors" field is to indicate what
text in the opinion the factor should be linked to (for instance, if the
factor is being displayed visually as an annotation to the opinion). In
this case, we simply placed the the full text where the anchor should be
placed. However, as we'll see later, we also could have used the
``TextQuoteSelector`` syntax from the ``anchorpoint`` module.

The pairs of curly brackets in the "content" field above also have
special meaning. A bracketed phrase in a ``content`` field identifies an
``Entity``. Typically an ``Entity`` is a person or party, but important
objects or concepts can also be labelled as class ``Entity``. If you
identify a phrase as an ``Entity`` by putting brackets around it, the
parser will recognize that phrase as the same Entity every time the
phrase appears, even if we don't put brackets around the other
instances. So when we choose the name of an ``Entity``, we need to make
sure the name is a unique word or phrase that always refers to the same
``Entity`` whenever it appears in the file.

If we need to include a bracket at the beginning or end of the text in
the "content" field, then we also need to put quote marks around the
text so the brackets won't be the first character. If the quote mark is
missing and a curly bracket is the first character of the text field,
then the parser won't understand that the field is supposed to be text.

Facts can also have ``truth`` fields. For instance, because this Fact
contains ``truth: false``, its meaning is reversed, so it now means "it
is False that Turismo Costa Brava was a domestic financial institution".

::

      - type: fact
        content: Turismo Costa Brava was a domestic financial institution
        truth: false

Enactments in AuthoritySpoke YAML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's the ``enactments`` field from the main Holding in the
Mazza-Alaluf case. It only contains one Enactment:

::

        enactments:
          - node: /us/usc/t18/s1960/b/1/A
            anchors: state money transmitting licenses, see |18 U.S.C. § 1960(b)(1)(A)|

(In this example, the ``enactments`` field isn't prefixed with a hyphen,
because it's not the first field of a new Holding. However, the ``node``
field is prefixed with a hyphen, because it is the first field of a new
Enactment.)

The ``node`` field indicates the location of the statute text being
cited: USC title 18, section 1960(b)(1)(A). (The AuthoritySpoke API
currently only serves citations to the US Constitution or the United
States Code.) Like Factors, Enactments can also have ``anchors``. This
time, the ``anchors`` field contains added "\|" characters called pipes,
that look like vertical lines. These pipes are part of an optional
shorthand syntax for locating a text passage within the Opinion. The
purpose of the pipe characters is to split the quotation into a "prefix"
to the left of the first pipe, an "exact" text, and a "suffix" to the
right of the second pipe. Only the "exact" text is considered to be the
anchor for an annotation showing were the Enactment can be found. The
reason for also including a prefix and suffix is to make the text
selector unambiguous. If the "exact" text of the anchor is the same as
text that appears somewhere else in the opinion, then the text anchor
can become unique by adding a unique prefix. Because the second pipe in
the ``anchors`` string has nothing after it, there is no suffix for this
text selector.

Instead of using the pipe syntax, enactments can also identify only part
of the text of a provision with "prefix", "exact", and "suffix" fields,
using the ``TextQuoteSelector`` data standard. Here's an example:

::

        enactments:
          - node: /us/usc/t18/s1960/b/1/A
            anchors:
              prefix: state money transmitting licenses, see
              exact: 18 U.S.C. § 1960(b)(1)(A)

The suffix field has been omitted because a suffix isn't needed to make
the text selector unique.

Even though the ``enactments`` field only contains one Enactment, the
``enactments_despite`` field contains one additional Enactment. This
means that the Holding applies "despite" the Enactment in that field. In
other words, the Holding rejects any argument that the Enactment will
change the outcome. This Enactment is a provision from Title 31 of the
United States Code, while the other Enactment was from Title 18.

::

        enactments_despite:
          - node: /us/usc/t31/s5312/b/1
            name: domestic institution statute

Holding Anchors
~~~~~~~~~~~~~~~

The holding also contains an ``anchors`` field that isn't nested inside
any Factor. This field represents the text anchor for the holding
itself. If this field is included, the holding anchor should be the
place in the opinion where the court indicates that it's endorsing the
legal rule stated in the holding, and accepting it as binding law in the
court's jurisdiction.

::

        anchors:
          - prefix: Accordingly, we conclude that the
            suffix: In any event

This time the ``anchors`` field uses another slightly different format.
The ``prefix`` and ``suffix`` for the text quote selector are includes
as separate lines in the YAML file, but the ``exact`` text of the anchor
passage has been omitted. Alternatively, we could have included the
``prefix`` and ``exact`` fields, but omitted the ``suffix``. We just
need to include enough information so the text selector can only
possibly refer to one location in the court opinion.

Booleans in YAML
~~~~~~~~~~~~~~~~

Holdings can also contain three true/false fields describing the legal
doctrine supported by the holding. All three of these fields default to
False, so they only need to be included in the file if they need to be
set to True. The fields are:

universal: whether the Holding applies in "all" situations where the
inputs are present

mandatory: whether the court "must" impose the results described in the
"outputs" field when the Holding applies. (In other words, "mandatory"
means "not discretionary")

exclusive: whether the inputs described by the Holding are the only way
to achieve the outputs. (For instance, if a Holding describes the
elements of a crime, it might also say that committing the elements of
the crime is the "exclusive" way for a person to be guilty of the
crime.)

Here's the complete ``holdings`` field of the YAML file, with all the
Factors filled in. Two boolean fields appear at the end.

::

    holdings:
      - inputs:
          - type: fact
            content: "{Mazza-Alaluf} operated {Turismo Costa Brava} without an appropriate money transmitting license in a State where such operation was punishable as a misdemeanor or a felony under State law"
            anchors: we conclude that sufficient evidence supports Mazza-Alaluf's convictions under 18 U.S.C. § 1960(b)(1)(A) for conspiring to operate and operating a money transmitting business without appropriate state licenses.
          - type: fact
            content: Mazza-Alaluf operated Turismo Costa Brava as a business
            anchors: Mazza-Alaluf does not contest that he owned and managed Turismo
          - type: fact
            content: Turismo Costa Brava was a money transmitting business
            anchors: record evidence that Turismo conducted substantial money transmitting business in the three states
        despite:
          - type: fact
            content: Turismo Costa Brava was a domestic financial institution
            truth: False
            anchors: without respect to whether or not Turismo was a "domestic financial institution"
        outputs:
          - type: fact
            content: Mazza-Alaluf committed the offense of conducting a money transmitting business without a license required by state law
            anchors: a crime to operate a money transmitting business without appropriate state licenses,
        enactments:
          - node: /us/usc/t18/s1960/b/1/A
            anchors: state money transmitting licenses, see |18 U.S.C. § 1960(b)(1)(A)|
        enactments_despite:
          - node: /us/usc/t31/s5312/b/1
            anchors:
              - § 5312(b)(1) (defining "domestic financial institution")
        anchors:
          - prefix: Accordingly, we conclude that the
            suffix: In any event
        universal: true
        mandatory: true

Loading Holdings from YAML
--------------------------

Let's save the example YAML above to a file, and then load the file with
AuthoritySpoke. Let's say the YAML file will be called ``myfile.yaml``,
and the path to that file from this notebook will be
``path/to/myfile.yaml``. In order to load not just the Holdings but also
the text anchors, we'll load the file using the
``read_holdings_with_anchors`` function. Notice that we're using the
"filepath" parameter instead of "filename".

.. code:: ipython3

    from authorityspoke.io.loaders import read_anchored_holdings_from_file
    holding_and_anchors = read_anchored_holdings_from_file(
        filepath="path/to/myfile.yaml",
        client=LEGIS_CLIENT)

.. code:: ipython3

    holding_from_yaml = holding_and_anchors.holdings[0]

Next, we'll print the holding we loaded to see how AuthoritySpoke
interpreted the YAML file.

.. code:: ipython3

    print(holding_from_yaml)


.. parsed-literal::

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
          "is operated without an appropriate money transmitting license in a State where such operation is punishable as a misdemeanor or a felony under State law, whether or not the defendant knew that the operation was required to be licensed or that the operation was so punishable;" (/us/usc/t18/s1960/b/1/A 2013-07-18)
        DESPITE the ENACTMENT:
          "“domestic financial agency” and “domestic financial institution” apply to an action in the United States of a financial agency or institution." (/us/usc/t31/s5312/b/1 2013-07-18)


The Holding that we created in Python and the Holding that we created in
YAML are both valid AuthoritySpoke objects. We can demonstrate this by
adding the two Holdings together to make a combined Holding that uses
information from both of them.

.. code:: ipython3

    combined_holding = holding_from_python + holding_from_yaml

.. code:: ipython3

    print(combined_holding)


.. parsed-literal::

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
        GIVEN the ENACTMENT:
          "the term “unlicensed money transmitting business” means a money transmitting business which affects interstate or foreign commerce in any manner or degree and— is operated without an appropriate money transmitting license in a State where such operation is punishable as a misdemeanor or a felony under State law, whether or not the defendant knew that the operation was required to be licensed or that the operation was so punishable;…" (/us/usc/t18/s1960/b/1 2013-07-18)
        DESPITE the ENACTMENT:
          "“domestic financial agency” and “domestic financial institution” apply to an action in the United States of a financial agency or institution." (/us/usc/t31/s5312/b/1 2013-07-18)


By combining the two Holdings, AuthoritySpoke has inferred that the Fact
that a defendant committed the New York offense can substitute for the
Fact that the defendant operated "without an appropriate money
transmitting license in a State where such operation was punishable as a
misdemeanor or a felony under State law". If the former Fact is
available, then the offense can be established even if the latter Fact
hasn't been found yet.

Assigning Names to Factors and Enactments in YAML
-------------------------------------------------

The YAML data input format is still verbose, but there's one more
feature we can use to shorten it. If a Factor or Enactment is going to
be used more than once in the same file, we can add a "name" field to
the YAML for that object. Then, anytime the same object needs to be
reused, we can just write the object's name rather than rewriting the
whole object. Similar to the names of Entities as discussed above, any
names assigned to Factors or Enactments need to be unique in the file.
They should only appear in the text of a ``content`` field if they're
intended to refer to the Factor or Enactment that has been given that
name.

Here's an example where the Holding we've been calling
``holding_from_python`` has been rewritten into the YAML file. Inside
that Holding, one Factor and one Enactment have been assigned
``name``\ s. Then, later in the file, the Factor and Enactment are
referenced by name instead of being rewritten in full. Here's the entire
updated YAML file. (This is the same as the file
``example_data/holdings/holding_mazza_alaluf.yaml``.)

holdings:

  - inputs:
    - type: fact
      content: "{Mazza-Alaluf} used Mazza-Alaluf's business {Turismo
      Costa Brava} to commit the New York offense of engaging in the
      business of receiving money for transmission or transmitting the same,
      without a license therefor"
    outputs:
    - type: fact
      content: Mazza-Alaluf operated Turismo Costa Brava without an
      appropriate money transmitting license in a State where such operation
      was punishable as a misdemeanor or a felony under State law
      anchors: we conclude that sufficient evidence supports Mazza-Alaluf's convictions under 18 U.S.C. § 1960(b)(1)(A) for conspiring to operate and operating a money transmitting business without appropriate state licenses.
      name: operated without license
    enactment:
    - node: /us/usc/t18/s1960/b/1
    - anchors: state money transmitting licenses, see |18 U.S.C. § 1960(b)(1)(A)|
    - name: state money transmitting license provision
    universal: true

  - inputs:
      - operated without license
      - type: fact
        content: Mazza-Alaluf operated Turismo Costa Brava as a business
        anchors: Mazza-Alaluf does not contest that he owned and managed Turismo
      - type: fact
        content: Turismo Costa Brava was a money transmitting business
        anchors: record evidence that Turismo conducted substantial money transmitting business in the three states
    despite:
      - type: fact
        content: Turismo Costa Brava was a domestic financial institution
        truth: False
        anchors: without respect to whether or not Turismo was a "domestic financial institution"
    outputs:
      - type: fact
        content: Mazza-Alaluf committed the offense of conducting a money transmitting business without a license required by state law
        anchors: a crime to operate a money transmitting business without appropriate state licenses,
    enactments:
      - state money transmitting license provision
    enactments_despite:
      - node: /us/usc/t31/s5312/b/1
        anchors:
          - § 5312(b)(1) (defining "domestic financial institution")
    anchors:
      - prefix: Accordingly, we conclude that the
        suffix: In any event
    universal: true
    mandatory: true

In the YAML above, a Factor is assigned the name "operated without
license", and then the second time the Factor is used, it's referenced
just by the name "operated without license". In the same way, an
Enactment is assigned the name "state money transmitting license
provision".

Now when we load a file with this YAML, we'll get both Holdings.

.. code:: ipython3

    both_holdings_with_anchors = read_anchored_holdings_from_file(
        filename="holding_mazza_alaluf.yaml",
        client=LEGIS_CLIENT)
    len(both_holdings_with_anchors.holdings)




.. parsed-literal::

    2
