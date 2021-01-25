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

AuthoritySpoke is open source software (as well as `Ethical
Source <https://ethicalsource.dev/definition/>`__ software). That mean
you have the opportunity to reuse AuthoritySpoke in your own projects.
You can also `participate in its
development <https://github.com/mscarey/AuthoritySpoke>`__ by submitting
issues, bug reports, and pull requests.

Getting Example Data
-----------------------

AuthoritySpoke helps you work with three kinds of data: court opinions,
legislative enactments, and structured annotations of legal procedural
rules.

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
If you’ve installed AuthoritySpoke and you need access to the example
data files, you'll need to download them from the `GitHub
repository <https://github.com/mscarey/AuthoritySpoke>`__.

Importing the Package
------------------------

If you want to use AuthoritySpoke in your own Python environment, be
sure you have installed AuthoritySpoke using a command like
``pip install AuthoritySpoke`` on the command line. Visit `the Python
Package Index <https://pypi.org/project/AuthoritySpoke/>`__ for more
details.

With a Python environment activated, let’s import AuthoritySpoke by
running the cell below. If you’re running this code on your own machine
but you don’t want to obtain API keys or make real API calls over the
Internet, you can change the two ``True`` variables to ``False`` to
use fake versions of the APIs.

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

Optional: Skip the Downloads and Load Decisions from a File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use the cell below to access ``Decision`` objects from a file rather
than an API, be sure the ``USE_REAL_CASE_API`` variable is set to
``False``. This should work if you’re running the tutorial in a notebook
in a cloud environment like Binder, or if you’ve cloned AuthoritySpoke’s
GitHub repository to your hard drive and you’re using ``jupyter`` to run
the tutorial in from the ``notebooks`` folder of the repository. The
notebook will try to find the data for the fake APIs in the
``example_data`` folder alongside a ``notebooks`` folder where this
notebook is running.

.. code:: ipython3

    from authorityspoke.io.loaders import load_decision
    from authorityspoke.io.readers import read_decision

    if not USE_REAL_CASE_API:

        oracle_download = load_decision("oracle_h.json")
        lotus_download = load_decision("lotus_h.json")

Downloading and Importing Decisions
--------------------------------------

If you didn’t load court opinions from the GitHub repository as
described in section 1.1, then you’ll be using the Caselaw Access
Project (CAP) API to get court opinions to load into AuthoritySpoke. To
download full cases from CAP, you’ll need to `register for a CAP API
key <https://case.law/user/register/>`__.

One good way to use an API key in a Jupyter Notebook or other Python
working file is to save the API key in a file called ``.env``. The
``.env`` file should contain a line that looks like
``CAP_API_KEY=your-api-key-here``. Then you can use
the `dotenv <https://pypi.org/project/python-dotenv/>`__
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

If you already loaded an :class:`~authorityspoke.opinions.Opinion`
from a file, running the cells
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

  >>> oracle_download["name"]
  'ORACLE AMERICA, INC., Plaintiff-Appellant, v. GOOGLE INC., Defendant-Cross-Appellant'

Yes, this is the correct case name. But if we had provided the API key
and used the ``full_case`` flag, we could have received more
information, like whether there are any non-majority opinions in the
case, and the names of the opinion authors. So let’s request the
*Oracle* case with ``full_case=True``.

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

    >>> from authorityspoke.io.readers import read_decision
    >>> oracle = read_decision(oracle_download)

And take a look at the object we made.

    >>> print(oracle)
    Oracle America, Inc. v. Google Inc., 750 F.3d 1339 (2014-05-09)

    >>> lotus = read_decision(lotus_download)
    >>> print(lotus)
    Lotus Development Corp. v. Borland International, Inc., 49 F.3d 807 (1995-03-09)

One judicial :class:`~authorityspoke.decisions.Decision` can include
multiple :class:`~authorityspoke.opinions.Opinion`\s. The Lotus
:class:`~authorityspoke.decisions.Decision` has a concurring opinion
as well as a majority opinion.
Access the ``majority`` attribute of the :class:`~authorityspoke.decisions.Decision`
object to get the majority opinion.

    >>> print(lotus.majority)
    majority Opinion by STAHL, Circuit Judge.

Downloading Enactments
-------------------------

The interface for downloading legislation is a little different. First
you create a Client class that holds your API key. Then you can use the
:meth:`legislice.download.Client.fetch` method to fetch JSON
representing the provision at a
specified citation on a specified date (or the most recent version, if
you don’t specify a date). Or you can
use :meth:`legislice.download.Client.read`, which also
fetches the JSON but then loads it into an instance of
the :class:`~legislice.enactments.Enactment` class.

.. code:: ipython3

    from authorityspoke.io.downloads import Client, FakeClient

    if USE_REAL_LEGISLICE_API:

        LEGISLICE_API_TOKEN = os.getenv("LEGISLICE_API_TOKEN")
        legis_client = Client(api_token=LEGISLICE_API_TOKEN)

    else:
        legis_client = FakeClient.from_file("usc.json")



Importing and Exporting Legal Holdings
-----------------------------------------

Now we can link some legal analysis to each
majority :class:`~authorityspoke.opinions.Opinion` by
using :meth:`authorityspoke.decisions.Decision.posit`
or :meth:`authorityspoke.opinions.Opinion.posit`. The parameter we pass to
this function is a :class:`~authorityspoke.holdings.Holding` or list
of :class:`~authorityspoke.holdings.Holding`\s posited by the
:class:`~authorityspoke.opinions.Opinion`\. You can think of
a :class:`~authorityspoke.holdings.Holding` as a statement about whether
a :class:`~authorityspoke.rules.Rule` is or is not valid law.
A holding may exist in the abstract, or one or
more :class:`~authorityspoke.opinions.Opinion`\s may
:meth:`~authorityspoke.opinions.Opinion.posit` it, which
means that the :class:`~authorityspoke.opinions.Opinion` adopts
the :class:`~authorityspoke.holdings.Holding` as its own. An
:class:`~authorityspoke.opinions.Opinion` may posit more than
one :class:`~authorityspoke.holdings.Holding`\.

Sadly, the labor of creating data
about :class:`~authorityspoke.holdings.Holding`\s falls mainly to
the user rather than the computer, at least in this early version of
AuthoritySpoke. AuthoritySpoke
loads :class:`~authorityspoke.holdings.Holding`\s from structured
descriptions that need to be created outside of AuthoritySpoke as JSON
files. For more information on creating these JSON files, see
the :ref:`create_holding_data`.
The guide includes a :ref:`json_api_spec`
describing the required data format.

For now, this introduction will rely on example JSON files that have
already been created. AuthoritySpoke should find them and convert them
to AuthoritySpoke objects when we call
the :func:`~authorityspoke.io.loaders.load_and_read_holdings`
function. If you pass in a ``client`` parameter, AuthoritySpoke will
make calls to the API at
`authorityspoke.com <https://authorityspoke.com/>`__ to find and link
the statutes or other :class:`~legislice.enactments.Enactment`\s cited in
the :class:`~authorityspoke.holdings.Holding`\.

    >>> from authorityspoke.io.loaders import load_and_read_holdings
    >>> oracle_holdings = load_and_read_holdings("holding_oracle.json", client=legis_client)
    >>> print(oracle_holdings[0])
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <the Java API> was copyrightable
        GIVEN:
          the Fact it is false that <the Java API> was an original work
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)

You can also convert Holdings back to JSON, or to a Python dictionary,
using the :mod:`~authorityspoke.io.dump` module.

    >>> from authorityspoke.io.dump import to_json, to_dict
    >>> to_dict(oracle_holdings[0])["rule"]["procedure"]
    {'inputs': [{'predicate': {'sign': '',
        'content': '{} was an original work',
        'quantity': None,
        'truth': False},
      'name': 'false the Java API was an original work',
      'generic': False,
      'standard_of_proof': None,
      'anchors': [OrderedDict([('exact', 'a work must be “original”'),
                    ('prefix', ''),
                    ('suffix', '')])],
      'terms': [{'name': 'the Java API',
        'anchors': [],
        'plural': False,
        'generic': True,
        'type': 'Entity'}],
      'absent': False,
      'type': 'Fact'}],
    'outputs': [{'predicate': {'sign': '',
        'content': '{} was copyrightable',
        'quantity': None,
        'truth': False},
      'name': 'false the Java API was copyrightable',
      'generic': False,
      'standard_of_proof': None,
      'anchors': [OrderedDict([('exact', 'copyright protection.'),
                    ('prefix', 'must be “original” to qualify for '),
                    ('suffix', '')]),
        OrderedDict([('exact',
                      'whether the non-literal elements of a program “are protected'),
                    ('prefix', ''),
                    ('suffix', '')])],
      'terms': [{'name': 'the Java API',
        'anchors': [],
        'plural': False,
        'generic': True,
        'type': 'Entity'}],
      'absent': False,
      'type': 'Fact'}],
    'despite': []}


Linking Holdings to Opinions
-------------------------------

If you want annotation anchors to link each Holding to a passage in an
:class:`~authorityspoke.opinions.Opinion`\, you can use
the :func:`~authorityspoke.io.loaders.load_holdings_with_anchors` method. The
result is type of :py:class:`~typing.NamedTuple` called
:class:`~authorityspoke.opinions.AnchoredHoldings`\. You can pass
this NamedTuple as the only argument
to the :meth:`authorityspoke.decisions.Decision.posit` method
to assign the :class:`~authorityspoke.holdings.Holding`\s to the
majority :class:`~authorityspoke.opinions.Opinion` of a
:class:`~authorityspoke.decisions.Decision`.
This will also link the correct text passages from
the :class:`~authorityspoke.opinions.Opinion` to
each :class:`~authorityspoke.holdings.Holding`\.

    >>> from authorityspoke.io.loaders import load_holdings_with_anchors
    >>> oracle_holdings_with_anchors = load_holdings_with_anchors("holding_oracle.json", client=legis_client)
    >>> lotus_holdings_with_anchors = load_holdings_with_anchors("holding_lotus.json", client=legis_client)
    >>> oracle.posit(oracle_holdings_with_anchors)
    >>> lotus.posit(lotus_holdings_with_anchors)

You can pass either one Holding or a list of Holdings to
:meth:`authorityspoke.decisions.Decision.posit`.
The :meth:`~authorityspoke.decisions.Decision.posit` method also has a
``text_links`` parameter that takes a dict indicating what text spans in
the Opinion should be linked to which Holding.

Viewing an Opinion’s Holdings
--------------------------------

If you take a look in
`holding_oracle.json <https://github.com/mscarey/AuthoritySpoke/blob/master/example_data/holdings/holding_oracle.json>`__
in AuthoritySpoke’s git repository, you’ll see that it would be loaded
in Python as a :py:class:`list` of 20 :py:class:`dict`\s, each representing a
holding. (In case you aren't familiar with how Python handles JSON, the outer
square brackets represent the beginning and end of the list. The start and end of each
:py:class:`dict` in the list is shown by a matched pair of curly brackets.)

Let’s make sure that the :meth:`~authorityspoke.decisions.Decision.posit` method
linked all of those holdings to
our ``oracle`` :class:`~authorityspoke.holdings.Opinion` object.

    >>> len(oracle.holdings)
    20

Now let’s see the string representation of the AuthoritySpoke Holding
object we created from the structured JSON we saw above.

    >>> print(oracle.holdings[0])
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
precondition for a :class:`~authorityspoke.rules.Rule` to apply.
So the two preconditions that must
be present to apply this :class:`~authorityspoke.rules.Rule` are
“the Fact it is false that the Java API was an original work” and
the statutory text creating copyright protection.

It’s also important to notice that
a :class:`~authorityspoke.rules.Rule` can be purely hypothetical
from the point of view of the Opinion that posits it. In this case, the
court finds that there would be a certain legal significance if it was
“GIVEN” that ``it is false that <the Java API> was an original work``,
but the court isn’t going to find that precondition applies, so it’s
also not going to accept the “RESULT” that
``it is false that <the Java API> was copyrightable``.

We can also access just the inputs of a :class:`~authorityspoke.holdings.Holding`\, just the
:class:`~authorityspoke.enactments.Enactment`\s, etc.

    >>> print(oracle.holdings[0].inputs[0])
    the Fact it is false that <the Java API> was an original work


    >>> print(oracle.holdings[0].enactments[0])
    "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


Generic Factors
------------------

The two instances of the phrase “the Java API” are in angle brackets to
indicate that the Java API is a generic :class:`~authorityspoke.entities.Entity` mentioned
in the :class:`~authorityspoke.facts.Fact`\.

    >>> oracle.holdings[0].generic_factors
    [Entity(name='the Java API', generic=True, plural=False, anchors=[])]


A generic :class:`~authorityspoke.entities.Entity` is “generic”
in the sense that in the context of
the :class:`~authorityspoke.factors.Factor` where
the :class:`~authorityspoke.entities.Entity` appears, it could be replaced with
some other generic :class:`~authorityspoke.entities.Entity` without
changing the meaning of the
:class:`~authorityspoke.factors.Factor` or the :class:`~authorityspoke.rules.Rule` where it appears.

Let’s illustrate this idea with the first holding from the *Lotus*
case.

    >>> print(lotus.holdings[0])
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


What if we wanted to generalize
this :class:`~authorityspoke.holdings.Holding` about copyright and
apply it in a different context, such as a case about books or
television shows instead of computer programs? First we could look at
the “generic” :class:`~authorityspoke.factors.Factor`\s of
the :class:`~authorityspoke.holdings.Holding`, which were marked off in
angle brackets in the string representation of
the :class:`~authorityspoke.holdings.Holding`\.

    >>> lotus.holdings[0].generic_factors
    [Entity(name='Borland International', generic=True, plural=False, anchors=[]),
    Entity(name='the Lotus menu command hierarchy', generic=True, plural=False, anchors=[])]


The same :class:`~authorityspoke.rules.Rule`\s and
:class:`~authorityspoke.holdings.Holding`\s may be relevant to more than one
``Opinion``. Let’s try applying the idea from ``lotus.holdings[0]`` to a
different copyright case that’s also about a derivative work. In `Castle
Rock Entertainment, Inc. v. Carol Publishing Group
Inc. <https://en.wikipedia.org/wiki/Castle_Rock_Entertainment,_Inc._v._Carol_Publishing_Group_Inc.>`__
(1998), a United States Court of Appeals found that a publisher
infringed the copyright in the sitcom *Seinfeld* by publishing a trivia
book called *SAT: The Seinfeld Aptitude Test*.

Maybe we’d like to see how the :class:`~authorityspoke.holdings.Holding` from
the *Lotus* case could
have applied in the context of the *Castle Rock Entertainment* case,
under 17 USC 102. We can check that by using the
:meth:`~authorityspoke.holdings.Holding.new_context` method to replace
the generic factors from the
*Lotus* :class:`~authorityspoke.holdings.Holding`\. One way to do this
is by passing a tuple containing a list of factors that need to be replaced,
followed by a list of their replacements.

    >>> from authorityspoke import Entity
    >>> seinfeld_holding = lotus.holdings[0].new_context(
        terms_to_replace=[
                Entity("Borland International"),
                Entity("the Lotus menu command hierarchy"),
            ],
        changes=[Entity("Carol Publishing Group"), Entity("Seinfeld")]
    )

The :meth:`~authorityspoke.holdings.Holding.new_context` method
returns a new :class:`~authorityspoke.holdings.Holding` object,
which we’ve assigned to the name ``seinfeld_holding``, but
the :class:`~authorityspoke.holdings.Holding` that we
used as a basis for the new object also still exists, and it’s
unchanged.

    >>> print(seinfeld_holding)
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


Even though these :class:`~authorityspoke.holdings.Holding`\s have different
generic factors and don’t evaluate equal to one another,
the :meth:`~authorityspoke.holdings.Holding.means` method
shows that they have the same meaning. In other words, they both endorse
exactly the same legal Rule. If
Holding A :meth:`~authorityspoke.holdings.Holding.means` Holding B, then
Holding A also necessarily :meth:`~authorityspoke.holdings.Holding.implies` Holding B.

    >>> lotus.holdings[0] == seinfeld_holding
    False


    >>> lotus.holdings[0].means(seinfeld_holding)
    True


Enactment Objects and Implication
------------------------------------

Sometimes it’s useful to know whether
one :class:`~authorityspoke.rules.Rule`
or :class:`~authorityspoke.holdings.Holding`
implies another. Basically, one
legal :class:`~authorityspoke.holdings.Holding`
:meth:`~authorityspoke.holdings.Holding.implies` a second
:class:`~authorityspoke.holdings.Holding` if its meaning
entirely includes the meaning of the second
:class:`~authorityspoke.holdings.Holding`\. To illustrate this idea,
let’s look at the :class:`~authorityspoke.enactments.Enactment`
that needs to be present to support the :class:`~authorityspoke.holdings.Holding` at
``oracle.holdings[0]``.

    >>> copyright_provision = oracle.holdings[0].enactments[0]
    >>> print(copyright_provision)
    "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


The :class:`~legislice.enactments.Enactment` object refers to part of the text of subsection 102(a)
from `Title 17 of the United States
Code <https://www.copyright.gov/title17/>`__.

Next, let’s create a new :class:`~legislice.enactments.Enactment`
object representing a shorter
passage of text from the same provision. We select some text from the
provision by calling the :meth:`~legislice.enactments.Enactment.select`
method with the string "Copyright protection subsists, in accordance with this title,
in original works of authorship", which exactly
matches some text that can be found in subsection 102(a).

    >>> from authorityspoke import Enactment
    >>> from anchorpoint import TextQuoteSelector
    works_of_authorship_passage = (
        "Copyright protection subsists, in accordance with this title, "
        + "in original works of authorship"
    )
    works_of_authorship_clause = legis_client.read("/us/usc/t17/s102/a")
    works_of_authorship_clause.select(works_of_authorship_passage)

Now we can create a new :class:`~authorityspoke.holdings.Holding` object
that cites to our new :class:`~legislice.enactments.Enactment` object
rather than the old one. This time, instead of using the
:meth:`~authorityspoke.holdings.Holding.new_context` method to create
a new :class:`~authorityspoke.holdings.Holding` object,
we’ll use Python's built-in :py:func:`~copy.deepcopy` function. This method gives us an
identical copy of the :class:`~authorityspoke.holdings.Holding` that we can change without
changing the original. Then we can use
the :meth:`~authorityspoke.holdings.Holding.set_enactments` method to
change what :class:`~legislice.enactments.Enactment` is
cited by the new :class:`~authorityspoke.holdings.Holding`\.

    >>> from copy import deepcopy
    >>> holding_with_shorter_enactment = deepcopy(oracle.holdings[0])
    >>> holding_with_shorter_enactment.set_enactments(works_of_authorship_clause)
    >>> print(holding_with_shorter_enactment)
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <the Java API> was copyrightable
        GIVEN:
          the Fact it is false that <the Java API> was an original work
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship…" (/us/usc/t17/s102/a 2013-07-18)


Now let’s try comparing this new :class:`~authorityspoke.holdings.Holding`
with the real :class:`~authorityspoke.holdings.Holding` from
the *Oracle* case, to see whether one :meth:`~authorityspoke.holdings.Holding.implies`
the other. When
you’re comparing AuthoritySpoke objects, the greater than sign ``>``
means “implies, but is not equal to”.

    >>> holding_with_shorter_enactment > oracle.holdings[0]
    True

You can also use the greater than or equal sign ``>=`` to mean “implies
or is equal to”. You can also use lesser than signs to test whether an
object on the right side of the expression implies the object on the
left. Thus, ``<=`` would mean “is implied by or is equal to”.

    >>> holding_with_shorter_enactment <= oracle.holdings[0]
    False

By comparing the string representations of the
original :class:`~authorityspoke.holdings.Holding` from
the *Oracle* case and ``holding_with_shorter_enactment``, can you tell
why the latter implies the former, and not the other way around?

If you guessed that it was because ``holding_with_shorter_enactment``
has a shorter :class:`~legislice.enactments.Enactment`\, you’re right.
A :class:`~authorityspoke.rules.Rule` that requires
fewer, or less specific, inputs is *broader* than
a :class:`~authorityspoke.rules.Rule` that has
more inputs, because there’s a larger set of situations where the
:class:`~authorityspoke.rules.Rule` can be triggered.

If this relationship isn’t clear to you, imagine some “Enactment A”
containing only a subset of the text of “Enactment B”, and then imagine
what would happen if a legislature amended some of the statutory text
that was part of Enactment B but not of Enactment A. A requirement to
cite Enactment B would no longer be possible to satisfy, because some of
that text would no longer be available. Thus a requirement to cite
Enactment A could be satisfied in every situation where a requirement to
cite Enactment B could be satisfied, and then some.

Checking for Contradictions
------------------------------

Let’s turn back to the *Lotus* case.

It says that under a statute providing that “In no case does copyright
protection for an original work of authorship extend to any…method of
operation”, the fact that a Lotus menu command hierarchy was a “method
of operation” meant that it was also uncopyrightable, despite a couple
of :class:`~authorityspoke.facts.Fact`\s that might tempt some
courts to rule the other way.

    >>> print(lotus.holdings[6])
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
the *Oracle* majority opinion
:meth:`~authorityspoke.opinions.Opinion.contradicts` the *Lotus*
majority opinion. Let’s check.

    >>> oracle.contradicts(lotus)
    True

That’s good to know, but we don’t want to take it on faith that a
contradiction exists. Let’s use
the :meth:`~authorityspoke.opinions.Opinion.explain_contradiction` method to
find the contradictory :class:`~authorityspoke.holdings.Holding`\s posited
by the *Oracle* and *Lotus* cases, and to generate a rudimentary
explanation of why they contradict.

    >>> explanation = lotus.explain_contradiction(oracle)
    >>> print(explanation)
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

We can use the :meth:`~authorityspoke.holdings.Holding.explain_contradiction` method
directly on a :class:`~authorityspoke.holdings.Holding` to generate all
available :class:`~authorityspoke.explanations.Explanation`\s of why a
contradiction is possible between `lotus.holdings[6]` and
`oracle.holdings[10]`. Each :class:`~authorityspoke.explanations.Explanation`
includes a mapping that shows how the context factors of
the :class:`~authorityspoke.holdings.Holding` on the left can be mapped
onto the :class:`~authorityspoke.holdings.Holding` on the right.
The explanation we’ve already been
given is that these two :class:`~authorityspoke.holdings.Holding`\s
contradict each other if you
consider ‘the Lotus menu command hierarchy’ to be analagous to ‘the Java
API’. The other possible explanation AuthoritySpoke could have given
would have been that ‘the Lotus menu command hierarchy’ is analagous to
‘the Java language’. Let’s see if the other
possible :class:`~authorityspoke.explanations.Explanation`
also appears in ``explanations``.


    >>> explanations = list(lotus.holdings[6].explanations_contradiction(oracle.holdings[10]))
    >>> len(explanations)
    1

No, there’s only one :class:`~authorityspoke.explanations.Explanation`
given for how these rules can contradict each other.
(The :meth:`~authorityspoke.holdings.Holding.explain_contradiction` method
returns only one one :class:`~authorityspoke.explanations.Explanation`, but
:meth:`~authorityspoke.holdings.Holding.explanations_contradiction`
is a generator that yields every :class:`~authorityspoke.explanations.Explanation`
it can find.) If you read the *Oracle* case, is makes sense that ‘the
Lotus menu command hierarchy’ is not considered analagous to
‘the Java language’. The *Oracle* case is only
about infringing the copyright in the Java API, not the copyright in the
whole Java language. A statement about infringement of ‘the Java
language’ would be irrelevant, not contradictory.

But what exactly is the contradiction between the two ``Holding``\ s?

The first obvious contrast between ``lotus.holdings[6]`` and
``oracle.holdings[10]`` is that
the :class:`~authorityspoke.holdings.Holding` from the *Lotus* case is
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
:class:`~authorityspoke.rules.Rule`\s. The *Oracle* opinion says that
courts can sometimes accept the result ``the Fact that <the Java API>
was copyrightable`` despite
the :class:`~authorityspoke.facts.Fact` ``<the Java API> was a method
of operation``. The *Lotus* :class:`~authorityspoke.opinions.Opinion`
would consider that impossible.

By the way, AuthoritySpoke does not draw on any Natural Language
Understanding technologies to determine the meaning of
each :class:`~authorityspoke.facts.Fact`\.
AuthoritySpoke mostly won’t recognize
that :class:`~authorityspoke.facts.Fact`\s have the same
meaning unless their ``content`` values are exactly the same string. As
discussed above, they can also differ in their references to generic
factors, which are the phrases that appear in brackets when you use the
``str()`` command on them. Also, AuthoritySpoke has a limited ability
to compare numerical statements in :class:`~authorityspoke.facts.Fact`\s using
`pint <https://pint.readthedocs.io/en/stable/>`__, an amazing Python
library that performs dimensional analysis.

Adding Holdings to One Another
----------------------------------

To try out the addition operation, let’s load another case from the
``example_data`` folder.

    >>> feist = load_and_read_decision("feist_h.json")
    >>> feist.posit(load_holdings_with_anchors("holding_feist.json", client=legis_client))


`Feist Publications, Inc. v. Rural Telephone Service
Co. <https://en.wikipedia.org/wiki/Feist_Publications,_Inc.,_v._Rural_Telephone_Service_Co.>`__
was a case that held that the listings in a telephone directory did not
qualify as “an original work” and that only original works are eligible
for protection under the Copyright Act. This is a two-step analysis.

The first step results in
the :class:`~authorityspoke.facts.Fact` it is false that a generic
:class:`~authorityspoke.entities.Entity` was “an original work”:

    >>> print(feist.holdings[10])
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
further result of “absence of the Fact that” a
generic :class:`~authorityspoke.entities.Entity` was “copyrightable”.

    >>> print(feist.holdings[3])
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


In this situation, anytime the
first :class:`~authorityspoke.holdings.Holding` (feist.holdings[10]) is
applied, the second Holding (feist.holdings[3]) can be applied as well.
That means the two Holdings can be :meth:`~authorityspoke.holdings.Holding.__add__`\ed
together to make a single Holding that captures the whole process.

    >>> listings_not_copyrightable = feist.holdings[10] + feist.holdings[3]
    >>> print(listings_not_copyrightable)
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
``listings_not_copyrightable`` has
two :class:`~authorityspoke.factors.Factor`\s under its “RESULT”, not
just one. Notice that it doesn’t matter that the two original Holdings
reference different generic :class:`~authorityspoke.entities.Entity` objects
(“Rural’s telephone directory” versus “Rural’s telephone listings”).
Because they’re generic, they’re interchangeable for this purpose.

You might recall that oracle.holdings[0] also was also about the
relationship between originality and copyrightability. Let’s see what
happens when we add oracle.holdings[0] to feist.holdings[10].

    >>> print(feist.holdings[10] + oracle.holdings[0])
    None


Can you guess why it’s not possible to add these
two :class:`~authorityspoke.holdings.Holding`\s together?
Here’s a hint:

    >>> feist.holdings[10].exclusive
    False
    >>> oracle.holdings[0].exclusive
    False
    >>> feist.holdings[3].exclusive
    True

``feist.holdings[10]`` and ``oracle.holdings[0]`` are
both :class:`~authorityspoke.holdings.Holding`\s that
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

Set Operations with Holdings
--------------------------------

In AuthoritySpoke, the :meth:`~authorityspoke.holdings.Holding.__or__` operator
(the \| symbol) is an alias for the :meth:`~authorityspoke.holdings.Holding.union`
operation. This operation is different from
the :meth:`~authorityspoke.holdings.Holding.__add__`
operation, and it usually gives different results.

    >>> result_of_adding = feist.holdings[10] + feist.holdings[3]
    >>> result_of_union = feist.holdings[10] | feist.holdings[3]
    >>> result_of_adding == result_of_union
    False

Although the existence of the :meth:`~authorityspoke.holdings.Holding.union`
operation might suggest that there
should also be an intersection operation, an intersection operation
is not yet implemented in AuthoritySpoke 0.4.


Apply the :meth:`~authorityspoke.holdings.Holding.union` operator
to two :class:`~authorityspoke.holdings.Holding`\s to get a
new :class:`~authorityspoke.holdings.Holding`
with all of the inputs and all of the outputs of both of the two
original ``Holding``\s. However, you only get such a new ``Holding`` if
it can be inferred by accepting the truth of the two original
``Holding``\s. If ``self`` :meth:`~authorityspoke.holdings.Holding.contradicts`
``other``, the operation returns ``None``. Likewise, if the two original
``Holding``\ s both have the value ``False`` for the parameter
``universal``, the operation will return ``None`` if it’s possible that
the “SOME” cases where one of the original ``Holding``\s applies don’t
overlap with the “SOME” cases where the other applies.

In this example, we’ll look at a ``Holding`` from *Oracle*, then a
``Holding`` from *Feist*, and then
the :meth:`~authorityspoke.holdings.Holding.union` of both of them.

    >>> print(oracle.holdings[1])
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


    >>> print(feist.holdings[2])
    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the Fact it is false that <Rural's telephone directory> was
          copyrightable
        GIVEN:
          the Fact that <Rural's telephone directory> was an idea
        GIVEN the ENACTMENT:
          "To promote the Progress of Science and useful Arts, by securing for limited Times to Authors…the exclusive Right to their respective Writings…" (/us/const/article/I/8/8 1788-09-13)


    >>> print(oracle.holdings[1] | feist.holdings[2])
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

The :meth:`~authorityspoke.holdings.Holding.union` operator is useful
for searching for contradictions in a
collection of :class:`~authorityspoke.holdings.Holding`\s. When two
:class:`~authorityspoke.holdings.Holding`\s are combined
together with the union operator, their union might contradict other
Holdings that neither of the two original Holdings would
have contradicted on their own.
