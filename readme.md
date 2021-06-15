# AuthoritySpoke

[![CircleCI](https://circleci.com/gh/mscarey/AuthoritySpoke.svg?style=svg)](https://circleci.com/gh/mscarey/AuthoritySpoke) [![Coverage Status](https://coveralls.io/repos/github/mscarey/AuthoritySpoke/badge.svg?branch=master)](https://coveralls.io/github/mscarey/AuthoritySpoke?branch=master)

AuthoritySpoke is the first open source legal authority automation tool.

## Installing AuthoritySpoke

AuthoritySpoke is a Python package [available on PyPI](https://pypi.org/project/AuthoritySpoke/), so you can install it with pip:

```
$ pip install authorityspoke
```

AuthoritySpoke runs on Python versions 3.8 and up.

## Trying it Out

Even if you don't install AuthoritySpoke, you can try it out by clicking the Binder button below to interact with it through a Jupyter Notebook. If you use Binder, you'll be shown the directory structure of this repo. Navigate to the `notebooks` folder to find the tutorials.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/mscarey/authorityspoke-examples/trunk)

## An Example

(A more detailed version of this example is [in the documentation](https://authorityspoke.readthedocs.io/en/latest/guides/introduction.html).)

This example shows how to discover contradictory legal holdings in `Oracle America, Inc. v. Google Inc., 750 F.3d 1339` (a famous circuit court decision that dealt with a claim that the Android operating system infringed the copyright on the Java language) and `Lotus Development Corporation v. Borland International, 49 F.3d 807` (an older case about whether a user interface was copyrightable). Replicating this example on your own computer would require obtaining API keys from both the [Caselaw Access Project API](https://api.case.law/v1/) and the [AuthoritySpoke API](https://authorityspoke.com/).

AuthoritySpoke includes a download client for retrieving court decisions from the [Caselaw Access Project API](https://api.case.law/v1/). (Or copies of both opinions can be loaded from the `example_data` folder of this repository.)

```python
>>> import os
>>> from dotenv import load_dotenv
>>> from authorityspoke import CAPClient
>>> load_dotenv()
True
>>> CAP_API_KEY = os.getenv('CAP_API_KEY')
>>> case_client = CAPClient(api_token=CAP_API_KEY)
>>> oracle = case_client.read_cite(
...    cite="750 F.3d 1339", full_case=True)
>>> str(oracle)
'Oracle America, Inc. v. Google Inc., 750 F.3d 1339 (2014-05-09)'
>>> lotus = case_client.read_cite(
...    cite="49 F.3d 807", full_case=True)
>>> str(lotus)
'Lotus Development Corp. v. Borland International, Inc., 49 F.3d 807 (1995-03-09)'
```

AuthoritySpoke can be used to create structured annotations for these cases by bringing together data from two sources: user-created annotations for judicial holdings, and legislative quotations that can be downloaded from the API at [authorityspoke.com](https://authorityspoke.com/). The `example_data` folder contains example annotations for the holdings in several cases, including the _Oracle_ and _Lotus_ cases. The LegisClient class is also a download client, and it can be used to retrieve legislative quotations.

```python
>>> from authorityspoke.io.downloads import LegisClient
>>> from authorityspoke.io.loaders import read_holdings_from_file
>>> LEGISLICE_API_TOKEN = os.getenv("LEGISLICE_API_TOKEN")
>>> legis_client = LegisClient(api_token=LEGISLICE_API_TOKEN)
>>> oracle_holdings = read_holdings_from_file("holding_oracle.yaml", client=legis_client)
>>> lotus_holdings = read_holdings_from_file("holding_lotus.yaml", client=legis_client)
```

User-created annotations for judicial holdings can be linked to court decisions using the `posit` method.

```python
>>> oracle.posit(oracle_holdings)
>>> lotus.posit(lotus_holdings)
```

Now, each `Decision` has a `.contradicts` method that can return a boolean indicating whether its holdings conflict with the holdings of another `Decision`.

```python
>>> lotus.contradicts(oracle)
True
```

AuthoritySpoke has concluded that these decisions do contradict one another. That's good to know, but we don't want to take it on faith that a contradiction exists. We can use the `explain_contradiction` method to find the contradictory Holdings posited by the _Oracle_ and _Lotus_ cases, and to generate a rudimentary explanation of why they contradict.

```python
>>> explanation = lotus.explain_contradiction(oracle)
>>> str(explanation)
"""
Because <the Lotus menu command hierarchy> is like <the Java API>,
  the Holding to ACCEPT
    the Rule that the court MUST ALWAYS impose the
      RESULT:
        the fact it was false that <the Lotus menu command hierarchy> was copyrightable
      GIVEN:
        the fact that <the Lotus menu command hierarchy> was a method of operation
      DESPITE:
        the fact that a text described <the Lotus menu command hierarchy>
        the fact that <the Lotus menu command hierarchy> was an original work
      GIVEN the ENACTMENT:
        "In no case does copyright protection for an original work of authorship extend to any…method of operation…" (/us/usc/t17/s102/b 2013-07-18)
CONTRADICTS
  the Holding to ACCEPT
    the Rule that the court MUST SOMETIMES impose the
      RESULT:
        the fact that <the Java API> was copyrightable
      GIVEN:
        the fact that <the Java language> was a computer program
        the fact that <the Java API> was a set of application programming interface declarations
        the fact that <the Java API> was an original work
        the fact that <the Java API> was a non-literal element of <the Java language>
        the fact that <the Java API> was the expression of an idea
        the fact it was false that <the Java API> was essentially the only way to express the idea that it embodied
        the fact that <the Java API> was creative
        the fact that it was possible to use <the Java language> without copying <the Java API>
      DESPITE:
        the fact that <the Java API> was a method of operation
        the fact that <the Java API> contained short phrases
        the fact that <the Java API> became so popular that it was the industry standard
        the fact that there was a preexisting community of programmers accustomed to using <the Java API>
      GIVEN the ENACTMENT:
        "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
      DESPITE the ENACTMENTS:
        "In no case does copyright protection for an original work of authorship extend to any…method of operation…" (/us/usc/t17/s102/b 2013-07-18)
        "The following are examples of works not subject to copyright and applications for registration of such works cannot be entertained: Words and short phrases such as names, titles, and slogans; familiar symbols or designs; mere variations of typographic ornamentation, lettering or coloring; mere listing of ingredients or contents; Ideas, plans, methods, systems, or devices, as distinguished from the particular manner in which they are expressed or described in a writing;  Blank forms, such as time cards, graph paper, account books, diaries, bank checks, scorecards, address books, report forms, order forms and the like, which are designed for recording information and do not in themselves convey information; Works consisting entirely of information that is common property containing no original authorship, such as, for example: Standard calendars, height and weight charts, tape measures and rulers, schedules of sporting events, and lists or tables taken from public documents or other common sources. Typeface as typeface." (/us/cfr/t37/s202.1 1992-02-21)
"""
```

In other words, because "the Lotus menu command hierarchy" has a similar role in the _Lotus_ case to the role of "the Java API" in the _Oracle_ case, a Holding from the _Lotus_ case (identified by the text before the word "CONTRADICTS") contradicts a Holding from the _Oracle_ case (identified by the text after the word "CONTRADICTS").

## Learning about AuthoritySpoke

You can find the example above and much more information about using AuthoritySpoke in the [Introduction to AuthoritySpoke](notebooks/introduction.ipynb) Jupyter notebook.

You can also find static versions of the tutorial notebooks, the API documentation, and more [in the project documentation](https://authorityspoke.readthedocs.io/en/latest/).

## Contributing to AuthoritySpoke

All participants are expected to follow the [code of conduct](code_of_conduct.md). AuthoritySpoke uses the [Contributor Covenant, version 1.4](https://www.contributor-covenant.org/version/1/4/code-of-conduct.html).

Submitting a pull request or other code contribution to AuthoritySpoke requires acceptance of a [contributor license agreement](contributor_agreement.md). The agreement's provisions are based on the [Apache Software Foundation Individual Contributor License Agreement V2.0](http://www.apache.org/licenses/icla.pdf).
