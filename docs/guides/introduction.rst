
``Introduction``
======================================

    "Details, unnumbered, shifting, sharp, disordered, unchartable,
    jagged."

    Llewellyn, Karl N. *The Bramble Bush: On Our Law and Its Study* 106
    (Quid Pro 2012) (1930).

AuthoritySpoke is a Python package that will help you make legal
authority readable by computers.

This notebook will provide an overview of AuthoritySpoke's most
important features. AuthoritySpoke is still in an early alpha state, so
many features have yet to be implemented, and some others still have
limited functionality.

1. Importing the Package
------------------------

If you want to use AuthoritySpoke in your own Python environment, be
sure you have installed AuthoritySpoke using a command like
``pip install AuthoritySpoke`` on the command line. Visit `the Python
Package Index <https://pypi.org/project/AuthoritySpoke/>`__ for more
details.

With a Python environment activated, let's import AuthoritySpoke.

.. code-block:: python

    import authorityspoke

If you executed that cell with no error messages, then it worked!

If you got a message like ``No module named 'authorityspoke'``, then
AuthoritySpoke is probably not installed in your current Python
environment. In that case, check the `Python
documentation <https://docs.python.org/3/installing/index.html>`__ for
help.

2. Downloading and Importing Decisions
--------------------------------------

Now we need some court opinions to load into AuthoritySpoke. We can
collect these from the Case Access Project API, a project of the Harvard
Law School Library Innovation Lab. To download full cases from CAP,
you'll need to `register for an API
key <https://case.law/user/register/>`__. However, if you'd rather skip
forward to the end of this section without interacting with the API,
then just go to section 2.1 below. There's already a copy of the files
we're going to download in the "example\_data/opinions" folder of this
repository.

The CAP API limits users to downloading 500 full cases per day. If you
accidentally make a query that returns hundreds of full cases, you could
hit your limit before you know it. You should first try out your API
queries without the "full\_case": "true" parameter, and then only
request full cases once you're confident you'll receive what you expect.
To minimize the risk of revealing your API key to others, you can store
it in an environment variable called CAP\_API\_KEY and then retrieve it
as shown in the cell below.

If you're viewing this tutorial in a cloud environment like Binder, you
could either replace ``os.environ['CAP_API_KEY']`` with a string
containing your own API key, or skip the use of the API key as described
below in section 2.1.

.. code-block:: python

    import os

    CAP_API_KEY = os.environ['CAP_API_KEY']

Next we need to download some cases for our analysis.

Let's download *Oracle America v. Google*, 750 F.3d 1339 (2014),
a landmark opinion in which the Federal Circuit Court of Appeals
held that the API declarations for the Java language were copyrightable.
And since we'll want to compare the *Oracle* case to a related case,
let's also download *Lotus Development Corporation v. Borland
International*, 49 F.3d 807 (1995). In that case, the First Circuit
Court of Appeals held that the menu structure of a spreadsheet program
called Lotus 1-2-3 was uncopyrightable because it was a
"method of operation" under the Copyright Act. As we'll see, the
*Oracle* case discusses and disagrees with the *Lotus* case.

.. code-block:: python

    from authorityspoke.io.downloads import download_case

    oracle_download = download_case(cite="750 F.3d 1339", filename="oracle_h.json")

Now we have a record representing the *Oracle* case, which has been
saved to the "example\_data/opinions" folder under the filename
"oracle\_h.json". Let's look at the API response.

.. code-block:: python

    from pprint import pprint
    pprint(oracle_download)


.. code-block:: none

    {'citations': [{'cite': '750 F.3d 1339', 'type': 'official'}],
     'court': {'id': 8955,
               'name': 'United States Court of Appeals for the Federal Circuit',
               'name_abbreviation': 'Fed. Cir.',
               'slug': 'fed-cir',
               'url': 'https://api.case.law/v1/courts/8955/'},
     'decision_date': '2014-05-09',
     'docket_number': 'Nos. 2013-1021, 2013-1022',
     'first_page': '1339',
     'frontend_url': 'https://cite.case.law/f3d/750/1339/',
     'id': 4066790,
     'jurisdiction': {'id': 39,
                      'name': 'U.S.',
                      'name_long': 'United States',
                      'slug': 'us',
                      'url': 'https://api.case.law/v1/jurisdictions/us/',
                      'whitelisted': False},
     'last_page': '1381',
     'name': 'ORACLE AMERICA, INC., Plaintiff-Appellant, v. GOOGLE INC., '
             'Defendant-Cross-Appellant',
     'name_abbreviation': 'Oracle America, Inc. v. Google Inc.',
     'reporter': {'full_name': 'Federal Reporter 3d Series',
                  'id': 933,
                  'url': 'https://api.case.law/v1/reporters/933/'},
     'url': 'https://api.case.law/v1/cases/4066790/',
     'volume': {'barcode': '32044132273806',
                'url': 'https://api.case.law/v1/volumes/32044132273806/',
                'volume_number': '750'}}


Yes, this is the case I expected. But if I had provided my API key and
used the full\_case flag, I could have received more information, like
whether there are any non-majority opinions in the case, and the names
of the opinion authors. So let's request the *Oracle* case with
``full_case=True``.

.. code-block:: python

    oracle_download = download_case(
        cite="750 F.3d 1339",
        filename="oracle_h.json",
        full_case=True,
        api_key=CAP_API_KEY)

And then do the same for the *Lotus* case.

.. code-block:: python

    lotus_download = download_case(
        cite="49 F.3d 807",
        filename="lotus_h.json",
        full_case=True,
        api_key=CAP_API_KEY)

Now let's convert the *Oracle* API response to an AuthoritySpoke object.

.. code-block:: python

    from authorityspoke.io.readers import read_decision

    oracle = read_decision(oracle_download)

And take a look at the object we made.

.. code-block:: python

    print(oracle)


.. code-block:: none

    Oracle America, Inc. v. Google Inc., 750 F.3d 1339 (2014-05-09)


.. code-block:: python

    lotus = read_decision(lotus_download)
    print(lotus)


.. code-block:: none

    Lotus Development Corp. v. Borland International, Inc., 49 F.3d 807 (1995-03-09)


Finally, what should you do if you chose not to get an API key or were
unable to create the Decision objects from downloaded data? Use the
following commands to create the Decision objects from the files in the
``example_data/cases`` folder.

If you already did the steps above, you can skip the next cell and go to
section 3.

2.1 Skip the API and Just Load the Decisions
--------------------------------------------

.. code-block:: python

    # If you already downloaded Opinions from the API,
    # running this cell will overwrite them with example data.
    # You should be able to use the rest of the notebook either way.

    from authorityspoke.io.loaders import load_and_read_decision

    oracle = load_and_read_decision("oracle_h.json")
    lotus = load_and_read_decision("lotus_h.json")

3. Importing Codes
------------------

AuthoritySpoke does not currently interface with any API to retrieve
legislative codes, the way it connects to the CAP API to retrieve case
opinions. However, AuthoritySpoke can import legislative XML files as
Code objects ("Code" in the sense of a legislative code), if the XML
adheres to the United States Legislative Markup (USLM) format as used by
the United States Code. Although AuthoritySpoke does have functions to
import federal regulations and California statutes, which are not
published in USLM, those functions are still brittle and are currently
only suitable for creating test data.

.. code-block:: python

    from authorityspoke.io.loaders import load_code

    constitution = load_code("constitution.xml")
    usc17 = load_code("usc17.xml")
    cfr37 = load_code("cfr37.xml")

When multiple Codes are enacted in one country's legal system, the best
way to organize the Code objects is to create a Regime object
representing the country and link each of the Codes to the Regime
object.

.. code-block:: python

    from authorityspoke import Regime

    usa = Regime()

    usa.set_code(constitution)
    usa.set_code(usc17)
    usa.set_code(cfr37)


4. Linking Rules to Opinions
----------------------------

One judicial ``Decision`` can include multiple ``Opinion``\ s. The
*Lotus* Decision has a concurring opinion as well as a majority opinion.
Access the ``majority`` attribute of the Decision object to get the
majority opinion.

.. code-block:: python

    print(lotus.majority)


.. code-block:: none

    majority Opinion by STAHL, Circuit Judge.


Now we can link some legal analysis to each majority ``Opinion`` by
using ``Decision.posit`` or ``Opinion.posit``. The parameter we pass to
this function is a ``Holding`` or list of ``Holding``\ s posited by the
``Opinion``. A **Holding** is statement about whether a **Rule** is or
is not valid law. A ``Holding`` may exist in the abstract, or it may be
**posited** by one or more ``Opinion``\ s, which means that the
``Opinion`` adopts the ``Holding`` as its own. An ``Opinion`` may posit
more than one ``Holding``.

Sadly, the labor of creating data about ``Holding``\ s falls mainly to
the user rather than the computer, at least in this early version of
AuthoritySpoke. AuthoritySpoke loads ``Holding``\ s from structured
descriptions that need to be created outside of AuthoritySpoke as JSON
files.

An explanation of the interface for creating new ``Holding`` objects can
be found in the ``create_holding_data`` notebook in this folder. That
interface should continue to undergo major changes as AuthoritySpoke
moves beyond version 0.3.

For now, this introduction will rely on example JSON files that have
already been created. AuthoritySpoke should find them when we call the
``load_holdings`` function, and then use the ``readers.read_holdings``
function to convert the JSON to AuthoritySpoke objects. If you pass in a
``regime`` parameter, AuthoritySpoke can use it to find and link the
statutes or other ``Enactment``\ s cited in the ``Holding``.

.. code-block:: python

    from authorityspoke.io.loaders import load_and_read_holdings

    oracle.posit(*load_and_read_holdings("holding_oracle.json", regime=usa))
    lotus.posit(*load_and_read_holdings("holding_lotus.json", regime=usa))


The ``Opinion.posit()`` method will assign the ``Holding``\ s to each
majority ``Opinion``.

You can pass either one Holding or a list of Holdings to
``Opinion.posit()``. The ``Opinion.posit()`` method also has a
``text_links`` parameter that takes a dict indicating what text spans in
the Opinion should be linked to which Holding.

5. Viewing an Opinion's Holdings
--------------------------------

If you take a look in "holding\_oracle.json", you'll see that it's a
list of 20 holdings. (You can verify this by checking how many times the
string "inputs" appears in the file.)

Let's make sure that the .posit() method linked all of those holdings to
our ``oracle`` Opinion object.

.. code-block:: python

    len(oracle.holdings)


.. code-block:: none

    20



Now let's see the string representation of the AuthoritySpoke Holding
object we created from the structured JSON we saw above.

.. code-block:: python

    print(oracle.holdings[0])


.. code-block:: none

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


Instead of the terms "inputs" and "outputs" we saw in the JSON file, we
now have "GIVEN" and "RESULT". And the "RESULT" comes first, because
it's hard to understand anything else about a legal rule until you
understand what it does. Also, notice the separate heading "GIVEN the
ENACTMENT". This indicates that the existence of statutory text (or
another kind of enactment such as a constitution) can also be a
precondition for a ``Rule`` to apply. So the two preconditions that must
be present to apply this ``Rule`` are "the Fact it is false that the
Java API was an original work" and the statutory text creating copyright
protection.

It's also important to notice that a ``Rule`` can be purely hypothetical
from the point of view of the Opinion that posits it. In this case, the
court finds that there would be a certain legal significance if it was
"GIVEN" that ``it is false that <the Java API> was an original work``,
but the court isn't going to find that precondition applies, so it's
also not going to accept the "RESULT" that
``it is false that <the Java API> was copyrightable``.

We can also access just the inputs of a ``Holding``, just the
``Enactment``\ s, etc.

.. code-block:: python

    print(oracle.holdings[0].inputs[0])


.. code-block:: none

    the Fact it is false that <the Java API> was an original work


.. code-block:: python

    print(oracle.holdings[0].enactments[0])


.. code-block:: none

    "Copyright protection subsists, in accordance with this title, in
    original works of authorship fixed in any tangible medium of
    expression, now known or later developed, from which they can be
    perceived, reproduced, or otherwise communicated, either directly or
    with the aid of a machine or device." (Title 17, /us/usc/t17/s102/a)


6. Generic Factors
------------------

The two instances of the phrase "the Java API" are in angle brackets to
indicate that the Java API is a generic ``Entity`` mentioned in the
``Fact``.

.. code-block:: python

    oracle.holdings[0].generic_factors




.. code-block:: none

    [Entity(name='the Java API', generic=True, plural=False)]



A generic ``Entity`` is "generic" in the sense that in the context of
the ``Factor`` where the ``Entity`` appears, it could be replaced with
some other generic ``Entity`` without changing the meaning of the
``Factor`` or the ``Rule`` where it appears.

Let's illustrate this idea with the first ``Holding`` from the *Lotus*
case.

.. code-block:: python

    print(lotus.holdings[0])


.. code-block:: none

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
          "Copyright protection subsists, in accordance with this title, in
          original works of authorship fixed in any tangible medium of
          expression, now known or later developed, from which they can be
          perceived, reproduced, or otherwise communicated, either directly or
          with the aid of a machine or device." (Title 17, /us/usc/t17/s102/a)


What if we wanted to generalize this ``Holding`` about copyright and
apply it in a different context, maybe involving books or movies instead
of computer programs? First we could look at the "generic" ``Factor``\ s
of the ``Holding``, which were marked off in angle brackets in the
string representation of the ``Holding``.

.. code-block:: python

    lotus.holdings[0].generic_factors




.. code-block:: none

    [Entity(name='Borland International', generic=True, plural=False),
     Entity(name='the Lotus menu command hierarchy', generic=True, plural=False)]



The same ``Rule``\ s and ``Holding``\ s may be relevant to more than one
``Opinion``. Let's try applying the idea from ``lotus.holdings[0]`` to a
different copyright case that's also about a derivative work. In
`*Castle Rock Entertainment, Inc. v. Carol Publishing Group
Inc.* <https://en.wikipedia.org/wiki/Castle_Rock_Entertainment,_Inc._v._Carol_Publishing_Group_Inc.>`__
(1998), a United States Court of Appeals found that a publisher
infringed the copyright in the sitcom *Seinfeld* by publishing a trivia
book called *SAT: The Seinfeld Aptitude Test*.

Maybe we'd like to see how the ``Holding`` from the *Lotus* case could
have applied in the context of the *Castle Rock Entertainment* case,
under 17 USC 102. We can check that by using the
``Holding.new_context()`` method to replace the generic factors from the
*Lotus* ``Holding``.

.. code-block:: python

    from authorityspoke import Entity

    seinfeld_holding = lotus.holdings[0].new_context(
        {Entity('Borland International'): Entity('Carol Publishing Group'),
        Entity('the Lotus menu command hierarchy'): Entity("Seinfeld")}
    )

In AuthoritySpoke, Holding and Factor objects are "frozen" objects,
which means Python will try to prevent you from modifying the object
after it has been created. The ``new_context`` method returns a new
``Holding`` object, which we've assigned to the name
``seinfeld_holding``, but the ``Holding`` that we used as a basis for
the new object also still exists, and it's unchanged.

.. code-block:: python

    print(seinfeld_holding)


.. code-block:: none

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
          "Copyright protection subsists, in accordance with this title, in
          original works of authorship fixed in any tangible medium of
          expression, now known or later developed, from which they can be
          perceived, reproduced, or otherwise communicated, either directly or
          with the aid of a machine or device." (Title 17, /us/usc/t17/s102/a)


Even though these ``Holding``\ s have different generic factors and
don't evaluate equal to one another, the ``Holding.means()`` method
shows that they have the same meaning. In other words, they both endorse
exactly the same legal Rule. If Holding A ``means`` Holding B, then
Holding A also necessarily ``implies`` Holding B.

.. code-block:: python

    lotus.holdings[0] == seinfeld_holding




.. code-block:: none

    False



.. code-block:: python

    lotus.holdings[0].means(seinfeld_holding)




.. code-block:: none

    True



7. Enactment Objects and Implication
------------------------------------

Sometimes it's useful to know whether one ``Rule`` or ``Holding``
implies another. Basically, one legal ``Holding`` implies a second
``Holding`` if its meaning entirely includes the meaning of the second
``Holding``. To illustrate this idea, let's look at the ``Enactment``
that needs to be present to trigger the ``Holding`` at
``oracle.holdings[0]``.

.. code-block:: python

    copyright_provision = oracle.holdings[0].enactments[0]
    print(copyright_provision)


.. code-block:: none

    "Copyright protection subsists, in accordance with this title, in
    original works of authorship fixed in any tangible medium of
    expression, now known or later developed, from which they can be
    perceived, reproduced, or otherwise communicated, either directly or
    with the aid of a machine or device." (Title 17, /us/usc/t17/s102/a)


The ``Enactment`` object refers to a ``Code`` object, which is an
instance of an AuthoritySpoke class representing a code of laws.
Specifically, it refers to `Title 17 of the United States
Code <https://www.copyright.gov/title17/>`__.

.. code-block:: python

    usc = copyright_provision.code
    print(usc)


.. code-block:: none

    Title 17


Next, let's create a new ``Enactment`` object representing a shorter
passage of text from the same ``Code``.

.. code-block:: python

    from authorityspoke import Enactment
    from authorityspoke.selectors import TextQuoteSelector

    works_of_authorship_selector = TextQuoteSelector(

            exact=("Copyright protection subsists, in accordance with this title,"
                      + " in original works of authorship")
            )


    works_of_authorship_clause = Enactment(
               source="/us/usc/t17/s102/a", selector=works_of_authorship_selector,
                code=usc
    )

Now we can create a new ``Holding`` object that cites to our new
``Enactment`` object rather than the old one. This time, instead of
using the ``new_context`` method to create a new ``Holding`` object,
we'll use the ``evolve`` method. With the ``evolve`` method, instead of
specifying ``Factor``\ s that should be replaced wherever they're found,
we specify which attributes of the ``Rule`` object we want to replace,
and then specify what we want to replace those attributes' old values
with. This returns a new ``Holding`` object and doesn't change the
existing ``Holding``.

.. code-block:: python

    rule_with_shorter_enactment = oracle.holdings[0].evolve(
                {"enactments": works_of_authorship_clause}
            )

.. code-block:: python

    print(rule_with_shorter_enactment)


.. code-block:: none

    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <the Java API> was copyrightable
        GIVEN:
          the Fact it is false that <the Java API> was an original work
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in
          original works of authorship" (Title 17, /us/usc/t17/s102/a)


Now let's try comparing this new ``Rule`` with the real ``Rule`` from
the *Oracle* case, to see whether one implies the other. When you're
comparing AuthoritySpoke objects, the greater than sign ``>`` means
"implies, but is not equal to".

.. code-block:: python

    rule_with_shorter_enactment > oracle.holdings[0]




.. code-block:: none

    True



You can also use the greater than or equal sign ``>=`` to mean "implies
or is equal to". In logic, it's common to say that identical statements
also imply one another, so that would mean ``>=`` is the symbol that
really means "implies". ``<=`` can also be used, and it means "is
implied by or is equal to".

.. code-block:: python

    rule_with_shorter_enactment <= oracle.holdings[0]




.. code-block:: none

    False



By comparing the string representations of the original ``Rule`` from
the *Oracle* case and ``rule_with_shorter_enactment``, can you tell why
the latter implies the former, and not the other way around?

If you guessed that it was because ``rule_with_shorter_enactment`` has a
shorter ``Enactment``, you're right. ``Rule``\ s that require fewer, or
less specific, inputs are *broader* than ``Rule``\ s that have more
inputs, because there's a larger set of situations where those
``Rule``\ s can be triggered.

If this relationship isn't clear to you, imagine some "Enactment A"
containing only a subset of the text of "Enactment B", and then imagine
what would happen if a legislature amended some of the statutory text
that was part of Enactment B but not of Enactment A. A requirement to
cite Enactment B would no longer be possible to satisfy, because some of
that text would no longer be available. Thus a requirement to cite
Enactment A could be satisfied in every situation where a requirement to
cite Enactment B could be satisfied, and then some.

8. Checking for Contradictions
------------------------------

Let's turn back to the *Lotus* case.

It says that under a statute providing that "In no case does copyright
protection for an original work of authorship extend to any...method of
operation", the fact that a Lotus menu command hierarchy was a "method
of operation" meant that it was also uncopyrightable, despite a couple
of ``Fact``\ s that might tempt some courts to rule the other way.

.. code-block:: python

    print(lotus.holdings[6])


.. code-block:: none

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
        GIVEN the ENACTMENTS:
          "In no case does copyright protection for an original work of
          authorship extend to any" (Title 17, /us/usc/t17/s102/b)
          "method of operation" (Title 17, /us/usc/t17/s102/b)


*Lotus* was a case relied upon by Google in the *Oracle v. Google* case,
but Oracle was the winner in that decision. So we might wonder whether
the *Oracle* Opinion contradicts the *Lotus* Opinion. Let's check.

.. code-block:: python

    oracle.contradicts(lotus)




.. code-block:: none

    True



That's good to know, but we don't want to take it on faith that a
contradiction exists. Let's use the ``explain_contradiction`` method to
find the contradictory ``Holding``\ s posited by the *Oracle* and
*Lotus* cases, and to generate a rudimentary explanation of why they
contradict.

.. code-block:: python

    explanation = lotus.explain_contradiction(oracle)
    print(explanation)


.. code-block:: none

    an Explanation of why there is a contradiction between
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
          GIVEN the ENACTMENTS:
            "In no case does copyright protection for an original work of
            authorship extend to any" (Title 17, /us/usc/t17/s102/b)
            "method of operation" (Title 17, /us/usc/t17/s102/b)
    and
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
            "Copyright protection subsists, in accordance with this title, in
            original works of authorship fixed in any tangible medium of
            expression, now known or later developed, from which they can be
            perceived, reproduced, or otherwise communicated, either directly or
            with the aid of a machine or device." (Title 17, /us/usc/t17/s102/a)
          DESPITE the ENACTMENTS:
            "In no case does copyright protection for an original work of
            authorship extend to any" (Title 17, /us/usc/t17/s102/b)
            "method of operation" (Title 17, /us/usc/t17/s102/b)
            "The following are examples of works not subject to copyright and
            applications for registration of such works cannot be entertained: (a)
            Words and short phrases such as names, titles, and slogans;" (Code of
            Federal Regulations Title 37, /us/cfr/t37/s202.1)
    is that <the Lotus menu command hierarchy> is like <the Java API>


That's a really complicated holding! Good thing we have AuthoritySpoke
to help us grapple with it.

We can use the ``explanations_contradiction`` method directly on
``Holding``\ s to generate all available "explanations" of why a
contradiction is possible between these lotus.holdings[6] and
oracle.holdings[10]. Each ``Explanation`` includes a mapping that shows
how the context factors of the ``Holding`` on the left can be mapped
onto the ``Holding`` on the right. The explanation we've already been
given is that these two ``Holding``\ s contradict each other if you
consider 'the Lotus menu command hierarchy' to be analagous to 'the Java
API'. The other possible explanation AuthoritySpoke could have given
would have been that 'the Lotus menu command hierarchy' is analagous to
'the Java language'. Let's see if the other possible ``ContextRegister``
also appears in ``explanations``.

.. code-block:: python

    explanations = list(lotus.holdings[6].explanations_contradiction(oracle.holdings[10]))
    len(explanations)




.. code-block:: none

    1



No, there's only the one explanation of how these rules can contradict
each other. If you read the *Oracle* case, this makes sense. It's only
about infringing the copyright in the Java API, not the copyright in the
whole Java language. A statement about infringement of 'the Java
language' would be irrelevant, not contradictory.

But what exactly is the contradiction between the two ``Holding``\ s?

The first obvious contrast between ``lotus.holdings[6]`` and
``oracle.holdings[10]`` is that the ``Holding`` from the *Lotus* case is
relatively succinct and categorical. The *Lotus* court interprets
Section 102(b) of the Copyright Act to mean that if a work is a "method
of operation", it's simply impossible for that work to be copyrighted,
so it's not necessary to consider a lot of case-specific facts to reach
a conclusion.

The Federal Circuit's *Oracle* decision complicates that view
significantly. The Federal Circuit believes that the fact that an API
is, or hypothetically might be, a "method of operation" is only one of
many factors that a court can consider in deciding copyrightability. The
following quotation, repeated in the *Oracle* case, illustrates the
Federal Circuit's view.

    “Section 102(b) does not extinguish the protection accorded a
    particular expression of an idea merely because that expression is
    embodied in a method of operation.” *Mitel, Inc. v. Iqtel, Inc.*,
    124 F.3d 1366, 1372 (10th Cir.1997)

And that's why AuthoritySpoke finds a contradiction between these two
``Rule``\ s. The *Oracle* opinion says that courts can sometimes accept
the result ``the Fact that <the Java API> was copyrightable`` despite
the ``Fact`` ``<the Java API> was a method of operation``. The *Lotus*
Opinion would consider that impossible.

By the way, AuthoritySpoke isn't applying any sophisticated grammatical
parsing to understand the meaning of each Fact. AuthoritySpoke mostly
won't recognize that ``Fact``\ s have the same meaning unless their
``content`` values are exactly the same string. As discussed above, they
can also differ in their references to generic factors, which are the
phrases that appear in brackets when you use the ``print()`` command on
them. And AuthoritySpoke can also compare ``Fact``\ s based on an
optional numeric value that can come at the end of their content, but
that feature isn't demonstrated in this tutorial.

9. Adding Holdings
------------------

To try out the addition operation, let's load another case from the
``example_data`` folder.

.. code-block:: python

    feist = load_and_read_decision("feist_h.json")
    feist.posit(*load_and_read_holdings("holding_feist.json", regime=usa))


`*Feist Publications, Inc. v. Rural Telephone Service
Co.* <https://en.wikipedia.org/wiki/Feist_Publications,_Inc.,_v._Rural_Telephone_Service_Co.>`__
was a case that held that the listings in a telephone directory did not
qualify as "an original work" and that only original works are eligible
for protection under the Copyright Act. This is a two-step analysis.

The first step results in the Fact it is false that a generic Entity was
"an original work":

.. code-block:: python

    print(feist.holdings[10])


.. code-block:: none

    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact it is false that <Rural's telephone listings> were an
          original work
        GIVEN:
          the Fact that <Rural's telephone listings> were names, towns, and
          telephone numbers of telephone subscribers
        GIVEN the ENACTMENTS:
          "To promote the Progress of Science and useful Arts, by securing for
          limited Times to Authors" (Constitution of the United States,
          /us/const/article-I/8/8)
          "the exclusive Right to their respective Writings" (Constitution of
          the United States, /us/const/article-I/8/8)
          "Copyright protection subsists, in accordance with this title, in
          original works of authorship" (Title 17, /us/usc/t17/s102/a)
          "The copyright in a compilation" (Title 17, /us/usc/t17/s103/b)
          "extends only to the material contributed by the author of such work,
          as distinguished from the preexisting material employed in the work,
          and does not imply any exclusive right in the preexisting material."
          (Title 17, /us/usc/t17/s103/b)


And the second step relies on the result of the first step to reach the
further result of "absence of the Fact that" a generic Entity was
"copyrightable".

.. code-block:: python

    print(feist.holdings[3])


.. code-block:: none

    the Holding to ACCEPT that the EXCLUSIVE way to reach the fact that
    <Rural's telephone directory> was copyrightable is
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <Rural's telephone directory> was copyrightable
        GIVEN:
          the Fact that <Rural's telephone directory> was an original work
        GIVEN the ENACTMENTS:
          "To promote the Progress of Science and useful Arts, by securing for
          limited Times to Authors" (Constitution of the United States,
          /us/const/article-I/8/8)
          "the exclusive Right to their respective Writings" (Constitution of
          the United States, /us/const/article-I/8/8)
          "Copyright protection subsists, in accordance with this title, in
          original works of authorship" (Title 17, /us/usc/t17/s102/a)


In this situation, anytime the first Holding (feist.holdings[10]) is
applied, the second Holding (feist.holdings[3]) can be applied as well.
That means the two Holdings can be added together to make a single
Holding that captures the whole process.

.. code-block:: python

    listings_not_copyrightable = feist.holdings[10] + feist.holdings[3]
    print(listings_not_copyrightable)


.. code-block:: none

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
          "To promote the Progress of Science and useful Arts, by securing for
          limited Times to Authors" (Constitution of the United States,
          /us/const/article-I/8/8)
          "the exclusive Right to their respective Writings" (Constitution of
          the United States, /us/const/article-I/8/8)
          "Copyright protection subsists, in accordance with this title, in
          original works of authorship" (Title 17, /us/usc/t17/s102/a)
          "The copyright in a compilation" (Title 17, /us/usc/t17/s103/b)
          "extends only to the material contributed by the author of such work,
          as distinguished from the preexisting material employed in the work,
          and does not imply any exclusive right in the preexisting material."
          (Title 17, /us/usc/t17/s103/b)


The difference between ``feist.holdings[10]`` and the newly-created
Holding ``listings_not_copyrightable`` is that
``listings_not_copyrightable`` has two Factors under its "RESULT", not
just one. Notice that it doesn't matter that the two original Holdings
reference different generic Entities ("Rural's telephone directory"
versus "Rural's telephone listings"). Because they're generic, they're
interchangeable for this purpose.

You might recall that oracle.holdings[0] also was also about the
relationship between originality and copyrightability. Let's see what
happens when we add oracle.holdings[0] to feist.holdings[10].

.. code-block:: python

    print(feist.holdings[10] + oracle.holdings[0])


.. code-block:: none

    None


Can you guess why it's not possible to add these two Holdings together?
Here's a hint:

.. code-block:: python

    feist.holdings[10].exclusive




.. code-block:: none

    False



.. code-block:: python

    oracle.holdings[0].exclusive




.. code-block:: none

    False



.. code-block:: python

    feist.holdings[3].exclusive




.. code-block:: none

    True



``feist.holdings[10]`` and ``oracle.holdings[0]`` are both Holdings that
purport to apply in only "SOME" cases where the specified inputs are
present, while ``feist.holdings[3]`` purports to be the "EXCLUSIVE" way
to reach its output, which indicates a statement about "ALL" cases.

You can't infer that there's any situation where ``feist.holdings[10]``
and ``oracle.holdings[0]`` can actually be applied together, because
there might not be any overlap between the "SOME" cases where one
applies and the "SOME" cases where the other applies. But if
``feist.holdings[10]`` and ``feist.holdings[3]`` are both valid law,
then we know they can both apply together in any of the "SOME" cases
where ``feist.holdings[10]`` applies.

10. Set Operations with Holdings
--------------------------------

In AuthoritySpoke, the union operation is different from the addition
operation, and it usually gives different results.

.. code-block:: python

    result_of_adding = feist.holdings[10] + feist.holdings[3]
    result_of_union = feist.holdings[10] | feist.holdings[3]

    result_of_adding == result_of_union




.. code-block:: none

    False



Two set operations that can be meaningfully applied to AuthoritySpoke
objects are the union operation (using Python's \| operator) and the
intersection operation (not yet implemented in AuthoritySpoke 0.2).

For context, let's review how these operators apply to ordinary Python
sets. The union operator combines two sets by returning a new set with
all of the elements of either of the original sets.

.. code-block:: python

    {3, 4} | {1, 4, 5}




.. code-block:: none

    {1, 3, 4, 5}



The intersection operator returns a new set with only the elements that
were in both original sets.

.. code-block:: python

    {3, 4} & {1, 4, 5}




.. code-block:: none

    {4}



Apply the union operator to two ``Holding``\ s to get a new ``Holding``
with all of the inputs and all of the outputs of both of the two
original ``Holding``\ s. However, you only get such a new ``Holding`` if
it can be inferred by accepting the truth of the two original
``Holding``\ s. If the two original ``Holding``\ s contradict one
another, the operation returns ``None``. Likewise, if the two original
``Holding``\ s both have the value ``False`` for the parameter
``universal``, the operation will return ``None`` if it's possible that
the "SOME" cases where one of the original ``Holding``\ s applies don't
overlap with the "SOME" cases where the other applies.

In this example, we'll look at a ``Holding`` from *Oracle*, then a
``Holding`` from *Feist*, and then the union of both of them.

.. code-block:: python

    print(oracle.holdings[1])


.. code-block:: none

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
          "Copyright protection subsists, in accordance with this title, in
          original works of authorship fixed in any tangible medium of
          expression, now known or later developed, from which they can be
          perceived, reproduced, or otherwise communicated, either directly or
          with the aid of a machine or device." (Title 17, /us/usc/t17/s102/a)


.. code-block:: python

    print(feist.holdings[2])


.. code-block:: none

    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the Fact it is false that <Rural's telephone directory> was
          copyrightable
        GIVEN:
          the Fact that <Rural's telephone directory> was an idea
        GIVEN the ENACTMENTS:
          "To promote the Progress of Science and useful Arts, by securing for
          limited Times to Authors" (Constitution of the United States,
          /us/const/article-I/8/8)
          "the exclusive Right to their respective Writings" (Constitution of
          the United States, /us/const/article-I/8/8)


.. code-block:: python

    print(oracle.holdings[1] | feist.holdings[2])


.. code-block:: none

    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the Fact that <the Java API> was an original work
          the Fact it is false that <the Java API> was copyrightable
        GIVEN:
          the Fact that <the Java API> was independently created by the author,
          as opposed to copied from other works
          the Fact that <the Java API> possessed at least some minimal degree of
          creativity
          the Fact that <the Java API> was an idea
        GIVEN the ENACTMENTS:
          "the exclusive Right to their respective Writings" (Constitution of
          the United States, /us/const/article-I/8/8)
          "To promote the Progress of Science and useful Arts, by securing for
          limited Times to Authors" (Constitution of the United States,
          /us/const/article-I/8/8)
          "Copyright protection subsists, in accordance with this title, in
          original works of authorship fixed in any tangible medium of
          expression, now known or later developed, from which they can be
          perceived, reproduced, or otherwise communicated, either directly or
          with the aid of a machine or device." (Title 17, /us/usc/t17/s102/a)


It's not obvious that a litigant could really establish all the "GIVEN"
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

11. Nuances of Meaning in Holdings
----------------------------------

Let's look at one more sentence from the *Oracle* ``Opinion``, so I can
point out a few more design decisions AuthoritySpoke makes in
representing procedural ``Holding``\ s.

    In the Ninth Circuit, while questions regarding originality are
    considered questions of copyrightability, concepts of merger and
    scenes a faire are affirmative defenses to claims of infringement.

(The "merger" doctrine says that a work is deemed to be "merged" with an
uncopyrightable idea if it's essentially the only way to express the
idea. "Scenes a faire" is a concept applied mostly to works of fiction,
and it means that conventional genre tropes are not copyrightable.)

The quoted sentence is fairly ordinary, as court opinions go, but I
found several interesting challenges in creating structered data about
its procedural meaning.

1. The sentence describes what the law is "In the Ninth Circuit". You
   might remember that the court that issued the *Oracle* opinion was
   the Federal Circuit, not the Ninth Circuit. So the Federal Circuit is
   deciding what it thinks that the Ninth Circuit thinks that Congress
   meant by enacting the statute. The middle layer of this
   interpretation, in which the Federal Circuit attributes a belief to
   the Ninth Circuit, is simply absent from the AuthoritySpoke model of
   the ``Holding``. However, future updates to AuthoritySpoke might make
   it possible to capture this information.

2. The sentence uses the concept of an "affirmative defense", which
   generally means a defense that the defendant has the burden of proof
   to establish. I chose to model this concept by writing that if one of
   the facts that would establish the affirmative defense is present,
   then it could be established that the copyright was not infringed,
   but if they are both absent, then the copyright could have been
   infringed. I'm sure some legal experts would find this too
   simplistic, and would argue that it's not possible to formalize the
   concept of an affirmative defense without explicitly mentioning
   procedural concepts like a burden of proof.

3. The sentence seems to have something to say about what happens if
   either of two Factors are present, or if both of them are absent.
   That makes three different Rules. It's not ideal for one sentence to
   explode into multiple different Python objects when it's formalized,
   and it's worth wondering whether there would have been a way to pack
   all the information into a single object.

4. I noticed that the concept of a copyrighted work being "merged" or
   being a "scene a faire" are both characteristics intrinsic in the
   copyrighted work, and don't depend on the characteristics of the
   allegedly infringing work. So if a work that's "merged" or is a
   "scene a faire" can't be infringed, but those concepts aren't
   relevant to copyrightability, then that means there are some works
   that are "copyrightable" but that can never be infringed by any other
   work. I suspect that the court's interpretation of these legal
   categories could confuse future courts and parties, with the result
   that the "merger" or "scene a faire" concepts could fall through the
   cracks and be ignored. Would there be a useful way to have
   AuthoritySpoke flag such anomalies?

The three Holding objects used to represent the sentence from the
*Oracle* opinion can be found in the Example Holdings document below. They're
``oracle.holdings[11]`` through ``oracle.holdings[13]``.
