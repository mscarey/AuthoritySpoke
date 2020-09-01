..  _introduction:

An Introduction to AuthoritySpoke
======================================================

   “Details, unnumbered, shifting, sharp, disordered, unchartable,
   jagged.”

   Karl N. Llewellyn, *The Bramble Bush: On Our Law and Its Study* (1930).

AuthoritySpoke is a Python package that will help you make legal
authority readable by computers.

This notebook will provide an overview of AuthoritySpoke’s most
important features. AuthoritySpoke is still in an alpha state, so many
features have yet to be implemented, and some others still have limited
functionality.

AuthoritySpoke helps you work with three kinds of data: court opinions,
legislative enactments, and structured annotations of legal procedural
rules.


0. Getting Example Data
-----------------------

To help you obtain court opinions, AuthoritySpoke provides an interface
to the `Caselaw Access Project <https://case.law/>`__ API, a project of
the Harvard Law School Library Innovation Lab. You’ll need to `register
for an API key <https://case.law/user/register/>`__.

To provide you with legislation text, AuthoritySpoke imports the
`Legislice <https://pypi.org/project/legislice/>`__ Python package,
which provides an interface to the Legislice API at
`authorityspoke.com <https://authorityspoke.com/>`__. This API currently
provides access to recent versions of the United States Code, plus the
United States Constitution. You’ll need to `sign
up <https://authorityspoke.com/account/signup/>`__ for an account and
then obtain a Legislice API key from your account page. The Legislice
API key is not the same as the Caselaw Access Project API key.

As of version 0.4, you mostly have to create your own procedural rule
annotations, but the ``example_data`` folder of the `GitHub repository
for AuthoritySpoke <https://github.com/mscarey/AuthoritySpoke>`__
contains example annotations for several cases. The rest of this
tutorial depends on having access to the ``example_data`` folder, so if
you’re running the tutorial code interactively, you’ll need to either
clone the AuthoritySpoke repository to your computer and run the
tutorial from there, or else run the tutorial from a cloud environment
like
`Binder <https://mybinder.org/v2/gh/mscarey/AuthoritySpoke/master>`__.
If you’ve only installed AuthoritySpoke from ``pip``, you won’t have
access to the example data files.

1. Importing the Package
------------------------

If you want to use AuthoritySpoke in your own Python environment, be
sure you have installed AuthoritySpoke using a command like
``pip install AuthoritySpoke`` on the command line. Visit `the Python
Package Index <https://pypi.org/project/AuthoritySpoke/>`__ for more
details.

With a Python environment activated, let’s import AuthoritySpoke by
running the cell below. If you’re running this code on your own machine
but you don’t want to obtain API keys or make real API calls over the
Internet, you can change the two ``True`` variables to ``False``.

.. code:: ipython3

    import authorityspoke

    USE_REAL_CASE_API = True
    USE_REAL_LEGISLICE_API = True

If you executed that cell with no error messages, then it worked!

If you got a message like ``No module named 'authorityspoke'``, then
AuthoritySpoke is probably not installed in your current Python
environment. In that case, check the `Python
documentation <https://docs.python.org/3/installing/index.html>`__ for
help on installing modules.

1.1 Optional: Skip the Downloads and Load Decisions from a File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use the cell below to access ``Decision`` objects from a file rather
than an API, be sure the ``USE_REAL_CASE_API`` variable is set to
``False``. This should work if you’re running the tutorial in a notebook
in a cloud environment like Binder, or if you’ve cloned AuthoritySpoke’s
GitHub repository to your hard drive and you’re using ``jupyter`` to run
the tutorial in from the ``notebooks`` folder of the repository.

.. code:: ipython3

    from authorityspoke.io.loaders import load_decision
    from authorityspoke.io.readers import read_decision

    if not USE_REAL_CASE_API:

        oracle_download = load_decision("oracle_h.json")
        lotus_download = load_decision("lotus_h.json")

2. Downloading and Importing Decisions
--------------------------------------

If you didn’t load court opinions from the GitHub repository as
described in section 1.1, then you’ll be using the Caselaw Access
Project (CAP) API to get court opinions to load into AuthoritySpoke. To
download full cases from CAP, you’ll need to `register for a CAP API
key <https://case.law/user/register/>`__.

One good way to use an API key in a Jupyter Notebook or other Python
working file is to save the API key in a file called ``.env``. The
``.env`` file should contain a line that looks like
``CAP_API_KEY=your-api-key-here``. Then you can use the ``dotenv``
Python package to load the API key as an environment variable without
ever writing the API key in the notebook. That makes it easier to keep
your API key secret, even if you publish your copy of the notebook and
make it visible on the internet.

However, if you’re viewing this tutorial in a cloud environment like
Binder, you probably won’t be able to create an environment variable.
Instead, you could replace ``os.getenv('CAP_API_KEY')`` with a string
containing your own API key.

.. code:: ipython3

    import os
    from dotenv import load_dotenv
    load_dotenv()

    CAP_API_KEY = os.getenv('CAP_API_KEY')

Next we need to download some cases for analysis.

The CAP API limits users to downloading 500 full cases per day. If you
accidentally make a query that returns hundreds of full cases, you could
hit your limit before you know it. You should first try out your API
queries without the ``"full_case": "true"`` parameter, and then only
request full cases once you’re confident you’ll receive what you expect.

Let’s download Oracle America v. Google, 750 F.3d 1339 (2014), a
landmark opinion in which the Federal Circuit Court of Appeals held that
the interface of the Java language was copyrightable. And since we’ll
want to compare the Oracle case to a related case, let’s also download
Lotus Development Corporation v. Borland International, 49 F.3d 807
(1995). In that case, the First Circuit Court of Appeals held that the
menu structure of a spreadsheet program called Lotus 1-2-3 was
uncopyrightable because it was a “method of operation” under the
Copyright Act. As we’ll see, the Oracle case discusses and disagrees
with the Lotus case.

If you already loaded ``Opinion``\ s from a file, running the cells
below with ``USE_REAL_CASE_API`` set to True will attempt to overwrite
them with data from the API. You should be able to run the rest of the
tutorial code either way.

.. code:: ipython3

    from authorityspoke.io.downloads import download_case
    from authorityspoke.io.loaders import load_and_read_decision

    if USE_REAL_CASE_API:
        oracle_download = download_case(cite="750 F.3d 1339")

Now we have a record representing the *Oracle* case, which can also be
found in the “example_data/opinions” folder under the filename
“oracle_h.json”. Let’s look at a field from the API response.

.. code:: ipython3

    oracle_download["name"]




.. parsed-literal::

    'ORACLE AMERICA, INC., Plaintiff-Appellant, v. GOOGLE INC., Defendant-Cross-Appellant'



Yes, this is the case I expected. But if I had provided my API key and
used the full_case flag, I could have received more information, like
whether there are any non-majority opinions in the case, and the names
of the opinion authors. So let’s request the *Oracle* case with
``full_case=True``.

.. code:: ipython3

    if USE_REAL_CASE_API:
        oracle_download = download_case(
        cite="750 F.3d 1339",
        full_case=True,
        api_key=CAP_API_KEY)

And then do the same for the *Lotus* case.

.. code:: ipython3

    if USE_REAL_CASE_API:
        lotus_download = download_case(
        cite="49 F.3d 807",
        full_case=True,
        api_key=CAP_API_KEY)

Now let’s convert the *Oracle* API response to an AuthoritySpoke object.

.. code:: ipython3

    from authorityspoke.io.readers import read_decision

    oracle = read_decision(oracle_download)

And take a look at the object we made.

.. code:: ipython3

    print(oracle)


.. parsed-literal::

    Oracle America, Inc. v. Google Inc., 750 F.3d 1339 (2014-05-09)


.. code:: ipython3

    lotus = read_decision(lotus_download)
    print(lotus)


.. parsed-literal::

    Lotus Development Corp. v. Borland International, Inc., 49 F.3d 807 (1995-03-09)


One judicial ``Decision`` can include multiple ``Opinion``\ s. The Lotus
``Decision`` has a concurring opinion as well as a majority opinion.
Access the ``majority`` attribute of the ``Decision`` object to get the
majority opinion.

.. code:: ipython3

    print(lotus.majority)


.. parsed-literal::

    majority Opinion by STAHL, Circuit Judge.


3. Downloading Enactments
-------------------------

The interface for downloading legislation is a little different. First
you create a Client class that holds your API key. Then you can use the
``Client.fetch`` method to fetch JSON representing the provision at a
specified citation on a specified date (or the most recent version, if
you don’t specify a date). Or you can use ``Client.read``, which also
fetches the JSON but then loads it into an instance of the ``Enactment``
class.

.. code:: ipython3

    from legislice.download import Client
    from legislice.mock_clients import MOCK_USC_CLIENT

    if USE_REAL_LEGISLICE_API:

        LEGISLICE_API_TOKEN = os.getenv("LEGISLICE_API_TOKEN")
        legis_client = Client(api_token=LEGISLICE_API_TOKEN)

    else:
        legis_client = MOCK_USC_CLIENT


4. Importing and Exporting Legal Holdings
-----------------------------------------

Now we can link some legal analysis to each majority ``Opinion`` by
using ``Decision.posit`` or ``Opinion.posit``. The parameter we pass to
this function is a ``Holding`` or list of ``Holding``\ s posited by the
``Opinion``. You can think of a ``Holding`` as a statement about whether
a ``Rule`` is or is not valid law. A ``Holding`` may exist in the
abstract, or it may be **posited** by one or more ``Opinion``\ s, which
means that the ``Opinion`` adopts the ``Holding`` as its own. An
``Opinion`` may posit more than one ``Holding``.

Sadly, the labor of creating data about ``Holding``\ s falls mainly to
the user rather than the computer, at least in this early version of
AuthoritySpoke. AuthoritySpoke loads ``Holding``\ s from structured
descriptions that need to be created outside of AuthoritySpoke as JSON
files. For more information on creating these JSON files, see the `guide
to creating Holding
data <https://authorityspoke.readthedocs.io/en/latest/guides/create_holding_data.html>`__.
The guide includes a `JSON
specification <https://authorityspoke.readthedocs.io/en/latest/guides/create_holding_data.html#json-api-specification>`__
describing the required data format.

For now, this introduction will rely on example JSON files that have
already been created. AuthoritySpoke should find them and convert them
to AuthoritySpoke objects when we call the ``load_and_read_holdings``
function. If you pass in a ``client`` parameter, AuthoritySpoke will
make calls to the API at
`authorityspoke.com <https://authorityspoke.com/>`__ to find and link
the statutes or other ``Enactment``\ s cited in the ``Holding``.

.. code:: ipython3

    from authorityspoke.io.loaders import load_and_read_holdings

    oracle_holdings = load_and_read_holdings("holding_oracle.json", client=legis_client)
    print(oracle_holdings[0])


.. parsed-literal::

    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <the Java API> was copyrightable
        GIVEN:
          the Fact it is false that <the Java API> was an original work
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


You can also convert Holdings back to JSON, or to a Python dictionary,
using the ``dump`` module.

.. code:: ipython3

    from authorityspoke.io.dump import to_json, to_dict

    to_dict(oracle_holdings[0])["rule"]["procedure"]




.. parsed-literal::

    {'despite': [],
     'outputs': [{'predicate': {'quantity': None,
        'comparison': '',
        'truth': False,
        'content': '{} was copyrightable',
        'reciprocal': False},
       'context_factors': [{'anchors': [],
         'plural': False,
         'name': 'the Java API',
         'generic': True,
         'type': 'Entity'}],
       'anchors': [{'suffix': '',
         'prefix': 'must be “original” to qualify for ',
         'exact': 'copyright protection.'},
        {'suffix': '',
         'prefix': '',
         'exact': 'whether the non-literal elements of a program “are protected'}],
       'absent': False,
       'name': 'false the Java API was copyrightable',
       'standard_of_proof': None,
       'generic': False,
       'type': 'Fact'}],
     'inputs': [{'predicate': {'quantity': None,
        'comparison': '',
        'truth': False,
        'content': '{} was an original work',
        'reciprocal': False},
       'context_factors': [{'anchors': [],
         'plural': False,
         'name': 'the Java API',
         'generic': True,
         'type': 'Entity'}],
       'anchors': [{'suffix': '',
         'prefix': '',
         'exact': 'a work must be “original”'}],
       'absent': False,
       'name': 'false the Java API was an original work',
       'standard_of_proof': None,
       'generic': False,
       'type': 'Fact'}]}



5. Linking Holdings to Opinions
-------------------------------

If you want annotation anchors to link each Holding to a passage in the
Opinion, you can use the ``load_holdings_with_anchors`` method. The
result is type of NamedTuple called ``AnchoredHoldings``. You can pass
this NamedTuple as the only argument to the ``Opinion.posit()`` method
to assign the ``Holding``\ s to the majority ``Opinion``. This will also
link the correct text passages from the Opinion to each Holding.

.. code:: ipython3

    from authorityspoke.io.loaders import load_holdings_with_anchors

    oracle_holdings_with_anchors = load_holdings_with_anchors("holding_oracle.json", client=legis_client)
    lotus_holdings_with_anchors = load_holdings_with_anchors("holding_lotus.json", client=legis_client)

    oracle.posit(oracle_holdings_with_anchors)
    lotus.posit(lotus_holdings_with_anchors)

You can pass either one Holding or a list of Holdings to
``Opinion.posit()``. The ``Opinion.posit()`` method also has a
``text_links`` parameter that takes a dict indicating what text spans in
the Opinion should be linked to which Holding.

6. Viewing an Opinion’s Holdings
--------------------------------

If you take a look in
`holding_oracle.json <https://github.com/mscarey/AuthoritySpoke/blob/master/example_data/holdings/holding_oracle.json>`__
in AuthoritySpoke’s git repository, you’ll see that it’s a list of 20
holdings. (You can verify this by checking how many times the string
“inputs” appears in the file.)

Let’s make sure that the .posit() method linked all of those holdings to
our ``oracle`` Opinion object.

.. code:: ipython3

    len(oracle.holdings)




.. parsed-literal::

    20



Now let’s see the string representation of the AuthoritySpoke Holding
object we created from the structured JSON we saw above.

.. code:: ipython3

    print(oracle.holdings[0])


.. parsed-literal::

    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <the Java API> was copyrightable
        GIVEN:
          the Fact it is false that <the Java API> was an original work
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


Instead of the terms “inputs” and “outputs” we saw in the JSON file, we
now have “GIVEN” and “RESULT”. And the “RESULT” comes first, because
it’s hard to understand anything else about a legal rule until you
understand what it does. Also, notice the separate heading “GIVEN the
ENACTMENT”. This indicates that the existence of statutory text (or
another kind of enactment such as a constitution) can also be a
precondition for a ``Rule`` to apply. So the two preconditions that must
be present to apply this ``Rule`` are “the Fact it is false that the
Java API was an original work” and the statutory text creating copyright
protection.

It’s also important to notice that a ``Rule`` can be purely hypothetical
from the point of view of the Opinion that posits it. In this case, the
court finds that there would be a certain legal significance if it was
“GIVEN” that ``it is false that <the Java API> was an original work``,
but the court isn’t going to find that precondition applies, so it’s
also not going to accept the “RESULT” that
``it is false that <the Java API> was copyrightable``.

We can also access just the inputs of a ``Holding``, just the
``Enactment``\ s, etc.

.. code:: ipython3

    print(oracle.holdings[0].inputs[0])


.. parsed-literal::

    the Fact it is false that <the Java API> was an original work


.. code:: ipython3

    print(oracle.holdings[0].enactments[0])


.. parsed-literal::

    "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


7. Generic Factors
------------------

The two instances of the phrase “the Java API” are in angle brackets to
indicate that the Java API is a generic ``Entity`` mentioned in the
``Fact``.

.. code:: ipython3

    oracle.holdings[0].generic_factors




.. parsed-literal::

    [Entity(name='the Java API', generic=True, plural=False, anchors=[])]



A generic ``Entity`` is “generic” in the sense that in the context of
the ``Factor`` where the ``Entity`` appears, it could be replaced with
some other generic ``Entity`` without changing the meaning of the
``Factor`` or the ``Rule`` where it appears.

Let’s illustrate this idea with the first ``Holding`` from the *Lotus*
case.

.. code:: ipython3

    print(lotus.holdings[0])


.. parsed-literal::

    the Holding to ACCEPT that the EXCLUSIVE way to reach the fact that
    <Borland International> infringed the copyright in <the Lotus menu
    command hierarchy> is
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <Borland International> infringed the copyright in <the
          Lotus menu command hierarchy>
        GIVEN:
          the Fact that <the Lotus menu command hierarchy> was copyrightable
          the Fact that <Borland International> copied constituent elements of
          <the Lotus menu command hierarchy> that were original
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


What if we wanted to generalize this ``Holding`` about copyright and
apply it in a different context, such as a case about books or
television shows instead of computer programs? First we could look at
the “generic” ``Factor``\ s of the ``Holding``, which were marked off in
angle brackets in the string representation of the ``Holding``.

.. code:: ipython3

    lotus.holdings[0].generic_factors




.. parsed-literal::

    [Entity(name='Borland International', generic=True, plural=False, anchors=[]),
     Entity(name='the Lotus menu command hierarchy', generic=True, plural=False, anchors=[])]



The same ``Rule``\ s and ``Holding``\ s may be relevant to more than one
``Opinion``. Let’s try applying the idea from ``lotus.holdings[0]`` to a
different copyright case that’s also about a derivative work. In `Castle
Rock Entertainment, Inc. v. Carol Publishing Group
Inc. <https://en.wikipedia.org/wiki/Castle_Rock_Entertainment,_Inc._v._Carol_Publishing_Group_Inc.>`__
(1998), a United States Court of Appeals found that a publisher
infringed the copyright in the sitcom *Seinfeld* by publishing a trivia
book called *SAT: The Seinfeld Aptitude Test*.

Maybe we’d like to see how the ``Holding`` from the *Lotus* case could
have applied in the context of the *Castle Rock Entertainment* case,
under 17 USC 102. We can check that by using the
``Holding.new_context()`` method to replace the generic factors from the
*Lotus* ``Holding``. One way to do this is by passing a tuple containing
a list of factors that need to be replaced, followed by a list of their
replacements.

.. code:: ipython3

    from authorityspoke import Entity

    seinfeld_holding = lotus.holdings[0].new_context(
        (
            [
                Entity("Borland International"),
                Entity("the Lotus menu command hierarchy"),
            ],
            [Entity("Carol Publishing Group"), Entity("Seinfeld")],
        ),
    )

The ``new_context`` method returns a new ``Holding`` object, which we’ve
assigned to the name ``seinfeld_holding``, but the ``Holding`` that we
used as a basis for the new object also still exists, and it’s
unchanged.

.. code:: ipython3

    print(seinfeld_holding)


.. parsed-literal::

    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <Carol Publishing Group> infringed the copyright in
          <Seinfeld>
        GIVEN:
          the Fact that <Seinfeld> was copyrightable
          the Fact that <Carol Publishing Group> copied constituent elements of
          <Seinfeld> that were original
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


Even though these ``Holding``\ s have different generic factors and
don’t evaluate equal to one another, the ``Holding.means()`` method
shows that they have the same meaning. In other words, they both endorse
exactly the same legal Rule. If Holding A ``means`` Holding B, then
Holding A also necessarily ``implies`` Holding B.

.. code:: ipython3

    lotus.holdings[0] == seinfeld_holding




.. parsed-literal::

    False



.. code:: ipython3

    lotus.holdings[0].means(seinfeld_holding)




.. parsed-literal::

    True



8. Enactment Objects and Implication
------------------------------------

Sometimes it’s useful to know whether one ``Rule`` or ``Holding``
implies another. Basically, one legal ``Holding`` implies a second
``Holding`` if its meaning entirely includes the meaning of the second
``Holding``. To illustrate this idea, let’s look at the ``Enactment``
that needs to be present to trigger the ``Holding`` at
``oracle.holdings[0]``.

.. code:: ipython3

    copyright_provision = oracle.holdings[0].enactments[0]
    print(copyright_provision)


.. parsed-literal::

    "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


The ``Enactment`` object refers to part of the text of subsection 102(a)
from `Title 17 of the United States
Code <https://www.copyright.gov/title17/>`__.

Next, let’s create a new ``Enactment`` object representing a shorter
passage of text from the same provision. We select some text from the
provision by calling the ``select`` method with the string
``works_of_authorship_passage``, which exactly matches some text that
can be found in subsection 102(a).

.. code:: ipython3

    from authorityspoke import Enactment
    from anchorpoint import TextQuoteSelector

    works_of_authorship_passage = (
        "Copyright protection subsists, in accordance with this title, "
        + "in original works of authorship"
    )


    works_of_authorship_clause = legis_client.read("/us/usc/t17/s102/a")
    works_of_authorship_clause.select(works_of_authorship_passage)

Now we can create a new ``Holding`` object that cites to our new
``Enactment`` object rather than the old one. This time, instead of
using the ``new_context`` method to create a new ``Holding`` object,
we’ll use Python's built-in deepcopy method. This method gives us an
identical copy of the Holding object that we can change without
changing the original. Then we can use the set_enactments method to
change what Enactment is cited by the new Holding.

.. code:: ipython3

    from copy import deepcopy

    holding_with_shorter_enactment = deepcopy(oracle.holdings[0])
    holding_with_shorter_enactment.set_enactments(works_of_authorship_clause)

.. code:: ipython3

    print(holding_with_shorter_enactment)


.. parsed-literal::

    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <the Java API> was copyrightable
        GIVEN:
          the Fact it is false that <the Java API> was an original work
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship…" (/us/usc/t17/s102/a 2013-07-18)


Now let’s try comparing this new ``Holding`` with the real ``Holding``
from the *Oracle* case, to see whether one implies the other. When
you’re comparing AuthoritySpoke objects, the greater than sign ``>``
means “implies, but is not equal to”.

.. code:: ipython3

    holding_with_shorter_enactment > oracle.holdings[0]




.. parsed-literal::

    True



You can also use the greater than or equal sign ``>=`` to mean “implies
or is equal to”. You can also use lesser than signs to test whether an
object on the right side of the expression implies the object on the
left. Thus, ``<=`` would mean “is implied by or is equal to”.

.. code:: ipython3

    holding_with_shorter_enactment <= oracle.holdings[0]




.. parsed-literal::

    False



By comparing the string representations of the original ``Holding`` from
the *Oracle* case and ``holding_with_shorter_enactment``, can you tell
why the latter implies the former, and not the other way around?

If you guessed that it was because ``holding_with_shorter_enactment``
has a shorter ``Enactment``, you’re right. ``Rule``\ s that require
fewer, or less specific, inputs are *broader* than ``Rule``\ s that have
more inputs, because there’s a larger set of situations where those
``Rule``\ s can be triggered.

If this relationship isn’t clear to you, imagine some “Enactment A”
containing only a subset of the text of “Enactment B”, and then imagine
what would happen if a legislature amended some of the statutory text
that was part of Enactment B but not of Enactment A. A requirement to
cite Enactment B would no longer be possible to satisfy, because some of
that text would no longer be available. Thus a requirement to cite
Enactment A could be satisfied in every situation where a requirement to
cite Enactment B could be satisfied, and then some.

9. Checking for Contradictions
------------------------------

Let’s turn back to the *Lotus* case.

It says that under a statute providing that “In no case does copyright
protection for an original work of authorship extend to any…method of
operation”, the fact that a Lotus menu command hierarchy was a “method
of operation” meant that it was also uncopyrightable, despite a couple
of ``Fact``\ s that might tempt some courts to rule the other way.

.. code:: ipython3

    print(lotus.holdings[6])


.. parsed-literal::

    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the Fact it is false that <the Lotus menu command hierarchy> was
          copyrightable
        GIVEN:
          the Fact that <the Lotus menu command hierarchy> was a method of
          operation
        DESPITE:
          the Fact that a text described <the Lotus menu command hierarchy>
          the Fact that <the Lotus menu command hierarchy> was an original work
        GIVEN the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any…method of operation…" (/us/usc/t17/s102/b 2013-07-18)


*Lotus* was a case relied upon by Google in the *Oracle v. Google* case,
but Oracle was the winner in that decision. So we might wonder whether
the *Oracle* Opinion contradicts the *Lotus* Opinion. Let’s check.

.. code:: ipython3

    oracle.contradicts(lotus)




.. parsed-literal::

    True



That’s good to know, but we don’t want to take it on faith that a
contradiction exists. Let’s use the ``explain_contradiction`` method to
find the contradictory ``Holding``\ s posited by the *Oracle* and
*Lotus* cases, and to generate a rudimentary explanation of why they
contradict.

.. code:: ipython3

    explanation = lotus.explain_contradiction(oracle)
    print(explanation)


.. parsed-literal::

    EXPLANATION: Because <the Lotus menu command hierarchy> is like <the Java API>,
      the Holding to ACCEPT
        the Rule that the court MUST ALWAYS impose the
          RESULT:
            the Fact it is false that <the Lotus menu command hierarchy> was
            copyrightable
          GIVEN:
            the Fact that <the Lotus menu command hierarchy> was a method of
            operation
          DESPITE:
            the Fact that a text described <the Lotus menu command hierarchy>
            the Fact that <the Lotus menu command hierarchy> was an original work
          GIVEN the ENACTMENT:
            "In no case does copyright protection for an original work of authorship extend to any…method of operation…" (/us/usc/t17/s102/b 2013-07-18)
    CONTRADICTS
      the Holding to ACCEPT
        the Rule that the court MUST SOMETIMES impose the
          RESULT:
            the Fact that <the Java API> was copyrightable
          GIVEN:
            the Fact that <the Java language> was a computer program
            the Fact that <the Java API> was a set of application programming
            interface declarations
            the Fact that <the Java API> was an original work
            the Fact that <the Java API> was a non-literal element of <the Java
            language>
            the Fact that <the Java API> was the expression of an idea
            the Fact it is false that <the Java API> was essentially the only way
            to express the idea that it embodied
            the Fact that <the Java API> was creative
            the Fact that it was possible to use <the Java language> without
            copying <the Java API>
          DESPITE:
            the Fact that <the Java API> was a method of operation
            the Fact that <the Java API> contained short phrases
            the Fact that <the Java API> became so popular that it was the
            industry standard
            the Fact that there was a preexisting community of programmers
            accustomed to using <the Java API>
          GIVEN the ENACTMENT:
            "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
          DESPITE the ENACTMENTS:
            "In no case does copyright protection for an original work of authorship extend to any…method of operation…" (/us/usc/t17/s102/b 2013-07-18)
            "The following are examples of works not subject to copyright and applications for registration of such works cannot be entertained: Words and short phrases such as names, titles, and slogans; familiar symbols or designs; mere variations of typographic ornamentation, lettering or coloring; mere listing of ingredients or contents; Ideas, plans, methods, systems, or devices, as distinguished from the particular manner in which they are expressed or described in a writing;  Blank forms, such as time cards, graph paper, account books, diaries, bank checks, scorecards, address books, report forms, order forms and the like, which are designed for recording information and do not in themselves convey information; Works consisting entirely of information that is common property containing no original authorship, such as, for example: Standard calendars, height and weight charts, tape measures and rulers, schedules of sporting events, and lists or tables taken from public documents or other common sources. Typeface as typeface." (/us/cfr/t37/s202.1 1992-02-21)


That’s a really complicated holding! Good thing we have AuthoritySpoke
to help us grapple with it.

We can use the ``explanations_contradiction`` method directly on
``Holding``\ s to generate all available “explanations” of why a
contradiction is possible between these lotus.holdings[6] and
oracle.holdings[10]. Each ``Explanation`` includes a mapping that shows
how the context factors of the ``Holding`` on the left can be mapped
onto the ``Holding`` on the right. The explanation we’ve already been
given is that these two ``Holding``\ s contradict each other if you
consider ‘the Lotus menu command hierarchy’ to be analagous to ‘the Java
API’. The other possible explanation AuthoritySpoke could have given
would have been that ‘the Lotus menu command hierarchy’ is analagous to
‘the Java language’. Let’s see if the other possible ``Explanation``
also appears in ``explanations``. (The ``explain_contradiction`` method
returns only one one ``Explanation``, but ``explanations_contradiction``
returns all it can find.)

.. code:: ipython3

    explanations = list(lotus.holdings[6].explanations_contradiction(oracle.holdings[10]))
    len(explanations)




.. parsed-literal::

    1



No, there’s only the one explanation of how these rules can contradict
each other. If you read the *Oracle* case, this makes sense. It’s only
about infringing the copyright in the Java API, not the copyright in the
whole Java language. A statement about infringement of ‘the Java
language’ would be irrelevant, not contradictory.

But what exactly is the contradiction between the two ``Holding``\ s?

The first obvious contrast between ``lotus.holdings[6]`` and
``oracle.holdings[10]`` is that the ``Holding`` from the *Lotus* case is
relatively succinct and categorical. The *Lotus* court interprets
Section 102(b) of the Copyright Act to mean that if a work is a “method
of operation”, it’s simply impossible for that work to be copyrighted,
so it’s not necessary to consider a lot of case-specific facts to reach
a conclusion.

The Federal Circuit’s *Oracle* decision complicates that view
significantly. The Federal Circuit believes that the fact that an API
is, or hypothetically might be, a “method of operation” is only one of
many factors that a court can consider in deciding copyrightability. The
following quotation, repeated in the *Oracle* case, illustrates the
Federal Circuit’s view.

   “Section 102(b) does not extinguish the protection accorded a
   particular expression of an idea merely because that expression is
   embodied in a method of operation.” Mitel, Inc. v. Iqtel, Inc., 124
   F.3d 1366, 1372 (10th Cir.1997)

And that’s why AuthoritySpoke finds a contradiction between these two
``Rule``\ s. The *Oracle* opinion says that courts can sometimes accept
the result ``the Fact that <the Java API> was copyrightable`` despite
the ``Fact`` ``<the Java API> was a method of operation``. The *Lotus*
Opinion would consider that impossible.

By the way, AuthoritySpoke does not draw on any Natural Language
Understanding technologies to determine the meaning of each ``Fact``.
AuthoritySpoke mostly won’t recognize that ``Fact``\ s have the same
meaning unless their ``content`` values are exactly the same string. As
discussed above, they can also differ in their references to generic
factors, which are the phrases that appear in brackets when you use the
``str()`` command on them. (Also, AuthoritySpoke has a limited ability
to compare numerical statements in ``Fact``\ s using
`pint <https://pint.readthedocs.io/en/stable/>`__, an amazing Python
library that performs dimensional analysis.)

10. Adding Holdings to One Another
----------------------------------

To try out the addition operation, let’s load another case from the
``example_data`` folder.

.. code:: ipython3

    feist = load_and_read_decision("feist_h.json")
    feist.posit(load_holdings_with_anchors("holding_feist.json", client=legis_client))


`Feist Publications, Inc. v. Rural Telephone Service
Co. <https://en.wikipedia.org/wiki/Feist_Publications,_Inc.,_v._Rural_Telephone_Service_Co.>`__
was a case that held that the listings in a telephone directory did not
qualify as “an original work” and that only original works are eligible
for protection under the Copyright Act. This is a two-step analysis.

The first step results in the ``Fact`` it is false that a generic
``Entity`` was “an original work”:

.. code:: ipython3

    print(feist.holdings[10])


.. parsed-literal::

    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact it is false that <Rural's telephone listings> were an
          original work
        GIVEN:
          the Fact that <Rural's telephone listings> were names, towns, and
          telephone numbers of telephone subscribers
        GIVEN the ENACTMENTS:
          "To promote the Progress of Science and useful Arts, by securing for limited Times to Authors…the exclusive Right to their respective Writings…" (/us/const/article/I/8/8 1788-09-13)
          "Copyright protection subsists, in accordance with this title, in original works of authorship…" (/us/usc/t17/s102/a 2013-07-18)
          "The copyright in a compilation…extends only to the material contributed by the author of such work, as distinguished from the preexisting material employed in the work, and does not imply any exclusive right in the preexisting material.…" (/us/usc/t17/s103/b 2013-07-18)


And the second step relies on the result of the first step to reach the
further result of “absence of the Fact that” a generic ``Entity`` was
“copyrightable”.

.. code:: ipython3

    print(feist.holdings[3])


.. parsed-literal::

    the Holding to ACCEPT that the EXCLUSIVE way to reach the fact that
    <Rural's telephone directory> was copyrightable is
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <Rural's telephone directory> was copyrightable
        GIVEN:
          the Fact that <Rural's telephone directory> was an original work
        GIVEN the ENACTMENTS:
          "To promote the Progress of Science and useful Arts, by securing for limited Times to Authors…the exclusive Right to their respective Writings…" (/us/const/article/I/8/8 1788-09-13)
          "Copyright protection subsists, in accordance with this title, in original works of authorship…" (/us/usc/t17/s102/a 2013-07-18)


In this situation, anytime the first Holding (feist.holdings[10]) is
applied, the second Holding (feist.holdings[3]) can be applied as well.
That means the two Holdings can be added together to make a single
Holding that captures the whole process.

.. code:: ipython3

    listings_not_copyrightable = feist.holdings[10] + feist.holdings[3]
    print(listings_not_copyrightable)


.. parsed-literal::

    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact it is false that <Rural's telephone listings> were an
          original work
          absence of the Fact that <Rural's telephone listings> were
          copyrightable
        GIVEN:
          the Fact that <Rural's telephone listings> were names, towns, and
          telephone numbers of telephone subscribers
        GIVEN the ENACTMENTS:
          "To promote the Progress of Science and useful Arts, by securing for limited Times to Authors…the exclusive Right to their respective Writings…" (/us/const/article/I/8/8 1788-09-13)
          "Copyright protection subsists, in accordance with this title, in original works of authorship…" (/us/usc/t17/s102/a 2013-07-18)
          "The copyright in a compilation…extends only to the material contributed by the author of such work, as distinguished from the preexisting material employed in the work, and does not imply any exclusive right in the preexisting material.…" (/us/usc/t17/s103/b 2013-07-18)


The difference between ``feist.holdings[10]`` and the newly-created
Holding ``listings_not_copyrightable`` is that
``listings_not_copyrightable`` has two Factors under its “RESULT”, not
just one. Notice that it doesn’t matter that the two original Holdings
reference different generic Entities (“Rural’s telephone directory”
versus “Rural’s telephone listings”). Because they’re generic, they’re
interchangeable for this purpose.

You might recall that oracle.holdings[0] also was also about the
relationship between originality and copyrightability. Let’s see what
happens when we add oracle.holdings[0] to feist.holdings[10].

.. code:: ipython3

    print(feist.holdings[10] + oracle.holdings[0])


.. parsed-literal::

    None


Can you guess why it’s not possible to add these two Holdings together?
Here’s a hint:

.. code:: ipython3

    feist.holdings[10].exclusive




.. parsed-literal::

    False



.. code:: ipython3

    oracle.holdings[0].exclusive




.. parsed-literal::

    False



.. code:: ipython3

    feist.holdings[3].exclusive




.. parsed-literal::

    True



``feist.holdings[10]`` and ``oracle.holdings[0]`` are both Holdings that
purport to apply in only “SOME” cases where the specified inputs are
present, while ``feist.holdings[3]`` purports to be the “EXCLUSIVE” way
to reach its output, which indicates a statement about “ALL” cases.

You can’t infer that there’s any situation where ``feist.holdings[10]``
and ``oracle.holdings[0]`` can actually be applied together, because
there might not be any overlap between the “SOME” cases where one
applies and the “SOME” cases where the other applies. But if
``feist.holdings[10]`` and ``feist.holdings[3]`` are both valid law,
then we know they can both apply together in any of the “SOME” cases
where ``feist.holdings[10]`` applies.

11. Set Operations with Holdings
--------------------------------

In AuthoritySpoke, the union operation is different from the addition
operation, and it usually gives different results.

.. code:: ipython3

    result_of_adding = feist.holdings[10] + feist.holdings[3]
    result_of_union = feist.holdings[10] | feist.holdings[3]

    result_of_adding == result_of_union




.. parsed-literal::

    False



Two set operations that can be meaningfully applied to AuthoritySpoke
objects are the union operation (using Python’s \| operator) and the
intersection operation (not yet implemented in AuthoritySpoke 0.3).

For context, let’s review how these operators apply to ordinary Python
sets. The union operator combines two sets by returning a new set with
all of the elements of either of the original sets.

.. code:: ipython3

    {3, 4} | {1, 4, 5}




.. parsed-literal::

    {1, 3, 4, 5}



The intersection operator returns a new set with only the elements that
were in both original sets.

.. code:: ipython3

    {3, 4} & {1, 4, 5}




.. parsed-literal::

    {4}



Apply the union operator to two ``Holding``\ s to get a new ``Holding``
with all of the inputs and all of the outputs of both of the two
original ``Holding``\ s. However, you only get such a new ``Holding`` if
it can be inferred by accepting the truth of the two original
``Holding``\ s. If the two original ``Holding``\ s contradict one
another, the operation returns ``None``. Likewise, if the two original
``Holding``\ s both have the value ``False`` for the parameter
``universal``, the operation will return ``None`` if it’s possible that
the “SOME” cases where one of the original ``Holding``\ s applies don’t
overlap with the “SOME” cases where the other applies.

In this example, we’ll look at a ``Holding`` from *Oracle*, then a
``Holding`` from *Feist*, and then the union of both of them.

.. code:: ipython3

    print(oracle.holdings[1])


.. parsed-literal::

    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the Fact that <the Java API> was an original work
        GIVEN:
          the Fact that <the Java API> was independently created by the author,
          as opposed to copied from other works
          the Fact that <the Java API> possessed at least some minimal degree of
          creativity
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


.. code:: ipython3

    print(feist.holdings[2])


.. parsed-literal::

    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the Fact it is false that <Rural's telephone directory> was
          copyrightable
        GIVEN:
          the Fact that <Rural's telephone directory> was an idea
        GIVEN the ENACTMENT:
          "To promote the Progress of Science and useful Arts, by securing for limited Times to Authors…the exclusive Right to their respective Writings…" (/us/const/article/I/8/8 1788-09-13)


.. code:: ipython3

    print(oracle.holdings[1] | feist.holdings[2])


.. parsed-literal::

    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the Fact it is false that <the Java API> was copyrightable
          the Fact that <the Java API> was an original work
        GIVEN:
          the Fact that <the Java API> was an idea
          the Fact that <the Java API> possessed at least some minimal degree of
          creativity
          the Fact that <the Java API> was independently created by the author,
          as opposed to copied from other works
        GIVEN the ENACTMENTS:
          "To promote the Progress of Science and useful Arts, by securing for limited Times to Authors…the exclusive Right to their respective Writings…" (/us/const/article/I/8/8 1788-09-13)
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


It’s not obvious that a litigant could really establish all the “GIVEN”
Factors listed above in a single case in a court where
``oracle.holdings[1]`` and ``feist.holdings[2]`` were both valid law,
but if they could, then it seems correct for AuthoritySpoke to conclude
that the court would have to find both
``the Fact that <the Java API> was an original work`` and
``the Fact it is false that <the Java API> was copyrightable``.

The union operator is useful for searching for contradictions in a
collection of ``Holding``\ s. When two ``Holding``\ s are combined
together with the union operator, their union might contradict other
``Holding``\ s that neither of the two original ``Holding``\ s would
have contradicted on their own.
