..  _example_holdings:

Example Annotated Holdings
======================================

In :ref:`introduction` and :ref:`create_holding_data`, we
practiced creating and exploring Python objects representing the
holdings of the cases Lotus v. Borland and Oracle v. Google.

This document is essentially an appendix to those two guides.
It contains a list of all of the :class:`~authorityspoke.holdings.Holding` objects in
``oracle.holdings`` and ``lotus.holdings``.
Each :class:`~authorityspoke.holdings.Holding` will be
preceded by a passage from the :class:`~authorityspoke.opinions.Opinion` that
indicates the opinion has endorsed
the :class:`~authorityspoke.holdings.Holding`\. In future versions,
AuthoritySpoke will give users the ability to explore the text passages
in :class:`~authorityspoke.opinions.Opinion`\s that provide support for
each :class:`~authorityspoke.holdings.Holding`\, but that’s
currently not fully implemented.

To find the full text of the opinions, look in the
`example_data/cases/ <https://github.com/mscarey/AuthoritySpoke/tree/master/example_data/cases>`__
folder of the AuthoritySpoke git repo.
The text delivered by the
`Caselaw Access Project API <https://case.law/api/>`__ was
collected from print sources, so it will contain some Optical
Character Recognition errors.

    >>> from authorityspoke.io.loaders import load_decision, read_holdings_from_file
    >>> from authorityspoke.io.readers import read_decision
    >>> lotus_download = load_decision("lotus_h.json")
    >>> lotus = read_decision(lotus_download)
    >>> USE_REAL_LEGISLICE_API = False
    >>> from authorityspoke.io.downloads import LegisClient
    >>> from authorityspoke.io.fake_enactments import FakeClient
    >>> if USE_REAL_LEGISLICE_API:
    ...     LEGISLICE_API_TOKEN = os.getenv("LEGISLICE_API_TOKEN")
    ...     legis_client = LegisClient(api_token=LEGISLICE_API_TOKEN)
    ... else:
    ...     legis_client = FakeClient.from_file("usc.json")


*Lotus v. Borland* 49 F.3d 807 (1995)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> lotus_holdings = read_holdings_from_file("holding_lotus.yaml", client=legis_client)
    >>> lotus.posit(lotus_holdings)

   To establish copyright infringement, a plaintiff must prove “(1)
   ownership of a valid copyright, and (2) copying of constituent
   elements of the work that are original.”

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


   To, show ownership of a valid copyright and therefore satisfy Feist’s
   first prong, a plaintiff must prove that the work as a whole is
   original and that the plaintiff complied with applicable statutory
   formalities.

    >>> print(lotus.holdings[1])
    the Holding to ACCEPT
      the Rule that the court MAY ALWAYS impose the
        RESULT:
          absence of the Fact that <the Lotus menu command hierarchy> was
          copyrightable
        GIVEN:
          absence of the Fact that <the Lotus menu command hierarchy> was an
          original work
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


   In judicial proceedings, a certificate of copyright registration
   constitutes prima facie evidence of copyrightability and shifts the
   burden to the defendant to demonstrate why the copyright is not
   valid.

    >>> print(lotus.holdings[2])
    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <the Lotus menu command hierarchy> was copyrightable
        GIVEN:
          the Evidence
            OF:
              the Exhibit in the FORM certificate of copyright registration
            INDICATING:
              the Fact that <Lotus Development Corporation> registered a copyright
              covering <the Lotus menu command hierarchy>
          absence of the Fact it is false that <the Lotus menu command
          hierarchy> was copyrightable
        GIVEN the ENACTMENT:
          "In any judicial proceedings the certificate of a registration made before or within five years after first publication of the work shall constitute prima facie evidence of the validity of the copyright and of the facts stated in the certificate. The evidentiary weight to be accorded the certificate of a registration made thereafter shall be within the discretion of the court." (/us/usc/t17/s410/c 2013-07-18)


   To show actionable copying and therefore satisfy Feist’s second
   prong, a plaintiff must first prove that the alleged infringer copied
   plaintiffs copyrighted work as a factual matter; to do this, he or
   she may either present direct evidence of factual copying or…

    >>> print(lotus.holdings[3])
    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <Borland International> copied <the Lotus menu command
          hierarchy> in creating <Quattro's Lotus Emulation Interface>
        GIVEN:
          the Evidence
            INDICATING:
              the Fact that <Borland International> copied <the Lotus menu command
              hierarchy> in creating <Quattro's Lotus Emulation Interface>
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


   To show actionable copying and therefore satisfy Feist’s second
   prong, a plaintiff must first prove that the alleged infringer copied
   plaintiffs copyrighted work as a factual matter; to do this, he or
   she may either present direct evidence of factual copying or, if that
   is unavailable, evidence that the alleged infringer had access to the
   copyrighted work and that the offending and copyrighted works are so
   similar that the court may infer that there was factual copying
   (i.e., probative similarity).


    >>> print(lotus.holdings[4])
    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <Borland International> copied <the Lotus menu command
          hierarchy> in creating <Quattro's Lotus Emulation Interface>
        GIVEN:
          the Evidence
            INDICATING:
              the Fact that <Borland International> had access to <the Lotus menu
              command hierarchy>
          the Fact that <Borland International> published <Quattro's Lotus
          Emulation Interface>
          the Evidence
            INDICATING:
              the Fact that <Quattro's Lotus Emulation Interface> was very similar
              to <the Lotus menu command hierarchy>
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


   To show actionable copying and therefore satisfy Feist’s second
   prong, a plaintiff must first prove that the alleged infringer copied
   plaintiffs copyrighted work as a factual matter…The plaintiff must
   then prove that the copying of copyrighted material was so extensive
   that it rendered the offending and copyrighted works substantially
   similar.

    >>> print(lotus.holdings[5])
    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <Borland International> copied constituent elements of
          <the Lotus menu command hierarchy> that were original
        GIVEN:
          the Fact that <Borland International> copied <the Lotus menu command
          hierarchy> in creating <Quattro's Lotus Emulation Interface>
          the Fact that the copying of <Quattro's Lotus Emulation Interface> in
          <the Lotus menu command hierarchy> was so extensive that it rendered
          them substantially similar
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


   Section 102(b) states: “In no case does copyright protection for an
   original work of authorship extend to any idea, procedure, process,
   system, method of operation, concept, principle, or discovery,
   regardless of the form in which it is described, explained,
   illustrated, or embodied in such work.” Because we conclude that the
   Lotus menu command hierarchy is a method of operation, we do not
   consider whether it could also be a system, process, or
   procedure…while original expression is necessary for copyright
   protection, we do not think that it is alone sufficient. Courts must
   still inquire whether original expression falls within one of the
   categories foreclosed from copyright protection by § 102(b), such as
   being a “method of operation.”

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


   We hold that the Lotus menu command hierarchy is an uneopyrightable
   “method of operation.” The Lotus menu command hierarchy provides the
   means by which users control and operate Lotus 1-2-3. If users wish
   to copy material, for example, they use the “Copy” command. If users
   wish to print material, they use the “Print” command. Users must use
   the command terms to tell the computer what to do. Without the menu
   command hierarchy, users would not be able to access and control, or
   indeed make use of, Lotus 1-2-3’s functional capabilities.

    >>> print(lotus.holdings[7])
    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <the Lotus menu command hierarchy> was a method of
          operation
        GIVEN:
          the Fact that <Lotus 1-2-3> was a computer program
          the Fact that <the Lotus menu command hierarchy> provided the means by
          which users controlled and operated <Lotus 1-2-3>
          the Fact that without <the Lotus menu command hierarchy>, users would
          not have been able to access and control, or indeed make use of,
          <Lotus 1-2-3>’s functional capabilities
          the Fact that for another computer program to by operated in
          substantially the same way as <Lotus 1-2-3>, the other program would
          have to copy <the Lotus menu command hierarchy>
        DESPITE:
          the Fact that the developers of <Lotus 1-2-3> made some expressive
          choices in choosing and arranging the terms in <the Lotus menu command
          hierarchy>
        GIVEN the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any…method of operation…" (/us/usc/t17/s102/b 2013-07-18)


   We do not think that “methods of operation” are limited to
   abstractions; rather, they are the means by which a user operates
   something.

    >>> print(lotus.holdings[8])
    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <the Lotus menu command hierarchy> was a method of
          operation
        GIVEN:
          the Fact that <the Lotus menu command hierarchy> was the means by
          which a person operated <Lotus 1-2-3>
        DESPITE:
          the Fact it is false that <the Lotus menu command hierarchy> was an
          abstraction
        GIVEN the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any…method of operation…" (/us/usc/t17/s102/b 2013-07-18)


   In other words, to offer the same capabilities as Lotus 1-2-3,
   Borland did not have to copy Lotus’s underlying code (and indeed it
   did not); to ’allow users to operate its programs in substantially
   the same way, however, Bor-land had to copy the Lotus menu command
   hierarchy. Thus the Lotus 1-2-3 code is not a uncopyrightable “method
   of operation.”

    >>> print(lotus.holdings[9])
    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact it is false that <Lotus 1-2-3> was a method of operation
        GIVEN:
          the Fact that <Lotus 1-2-3> was a computer program
          the Fact it is false that the precise formulation of <Lotus 1-2-3>'s
          code was necessary for it to work
        DESPITE:
          the Fact that computer code was necessary for <Lotus 1-2-3> to work
        GIVEN the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any…method of operation…" (/us/usc/t17/s102/b 2013-07-18)


*Oracle v. Google* 750 F.3d 1339 (2014)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> oracle_download = load_decision("oracle_h.json")
    >>> oracle = read_decision(oracle_download)
    >>> oracle_holdings = read_holdings_from_file("holding_oracle.yaml", client=legis_client)
    >>> oracle.posit(oracle_holdings)

   By statute, a work must be “original” to qualify for copyright
   protection. 17 U.S.C. § 102(a).

    >>> print(oracle.holdings[0])
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <the Java API> was copyrightable
        GIVEN:
          the Fact it is false that <the Java API> was an original work
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


   Original, as the term is used in copyright, means only that the work
   was independently created by the author (as opposed to copied from
   other works), and that it possesses at least some minimal degree of
   creativity.

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


   Copyright protection extends only to the expression of an idea — not
   to the underlying idea itself…In the Ninth Circuit, while questions
   regarding originality are considered questions of copyrightability,
   concepts of merger and scenes a faire are affirmative defenses to
   claims of infringement.

    >>> print(oracle.holdings[2])
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact that <the Java API> was copyrightable
        GIVEN:
          the Fact that <the Java API> was an original work
          the Fact that <the Java API> was the expression of an idea
          the Fact it is false that <the Java API> was an idea
        DESPITE:
          the Fact that <the Java API> was essentially the only way to express
          the idea that it embodied
          the Fact that <the Java API> was a scene a faire
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
        DESPITE the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)


   The literal elements of a computer program are the source code and
   object code.

    >>> print(oracle.holdings[3])
    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the Fact that <the Java API> was a literal element of <the Java
          language>
        GIVEN:
          the Fact that <the Java language> was a computer program
          the Fact that <the Java API> was the source code of <the Java
          language>
        GIVEN the ENACTMENTS:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)

    >>> print(oracle.holdings[4])
    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the Fact that <the Java API> was a literal element of <the Java
          language>
        GIVEN:
          the Fact that <the Java language> was a computer program
          the Fact that <the Java API> was the object code of <the Java
          language>
        GIVEN the ENACTMENTS:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)


   It is well established that copyright protection can extend to both
   literal and non-literal elements of a computer program. See Altai 982
   F.2d at 702.

    >>> print(oracle.holdings[5])
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact that <the Java API> was copyrightable
        GIVEN:
          the Fact that <the Java language> was a computer program
          the Fact that <the Java API> was a literal element of <the Java
          language>
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
        DESPITE the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)


   The non-literal components of a computer program include, among other
   things, the program’s sequence, structure, and organization, as well
   as the program’s user interface.

    >>> print(oracle.holdings[6])
    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the Fact that <the Java API> was a non-literal element of <the Java
          language>
        GIVEN:
          the Fact that <the Java language> was a computer program
          the Fact that <the Java API> was the sequence, structure, and
          organization of <the Java language>
        GIVEN the ENACTMENTS:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)

    >>> print(oracle.holdings[7])
    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the Fact that <the Java API> was a non-literal element of <the Java
          language>
        GIVEN:
          the Fact that <the Java language> was a computer program
          the Fact that <the Java API> was the user interface of <the Java
          language>
        GIVEN the ENACTMENTS:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)


   It is well established that copyright protection can extend to both
   literal and non-literal elements of a computer program…As discussed
   below, whether the non-literal elements of a program “are protected
   depends on whether, on the particular facts of each case, the
   component in question qualifies as an expression of an idea, or an
   idea itself.”


    >>> print(oracle.holdings[8])
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact that <the Java API> was copyrightable
        GIVEN:
          the Fact that <the Java language> was a computer program
          the Fact that <the Java API> was a non-literal element of <the Java
          language>
          the Fact that <the Java API> was the expression of an idea
          the Fact it is false that <the Java API> was an idea
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
        DESPITE the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)

    >>> print(oracle.holdings[9])
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <the Java API> was copyrightable
        GIVEN:
          the Fact that <the Java language> was a computer program
          the Fact that <the Java API> was a non-literal element of <the Java
          language>
          the Fact it is false that <the Java API> was the expression of an idea
          the Fact that <the Java API> was an idea
        GIVEN the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)
        DESPITE the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


   On appeal, Oracle argues that the district court’s reliance on Lotus
   is misplaced because it is distinguishable on its facts and is
   inconsistent with Ninth Circuit law. We agree. First, while the
   defendant in Lotus did not copy any of the underlying code, Google
   concedes that it copied portions of Oracle’s declaring source code
   verbatim. Second, the Lotus court found that the commands at issue
   there (copy, print, etc.) were not creative, but it is undisputed
   here that the declaring code and the structure and organization of
   the API packages are both creative and original. Finally, while the
   court in Lotus found the commands at issue were “essential to
   operating” the system, it is undisputed that— other than perhaps as
   to the three core packages — Google did not need to copy the
   structure, sequence, and organization of the Java API packages to
   write programs in the Java language.

   More importantly,
   however, the Ninth Circuit has not adopted the court’s “method of
   operation” reasoning in Lotus, and we conclude that it is
   inconsistent with binding precedent.

    >>> print(oracle.holdings[10])
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


   In the Ninth Circuit, while questions regarding originality are
   considered questions of copyrightability, concepts of merger and
   scenes a faire are affirmative defenses to claims of infringement.

    >>> print(oracle.holdings[11])
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <Google> infringed the copyright on <the
          Java API>
        GIVEN:
          the Fact that <the Java API> was a scene a faire
        DESPITE:
          the Fact that <the Java API> was copyrightable
        GIVEN the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)
        DESPITE the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


   In the Ninth Circuit, while questions regarding originality are
   considered questions of copyrightability, concepts of merger and
   scenes a faire are affirmative defenses to claims of
   infringement…Under the merger doctrine, a court will not protect a
   copyrighted work from infringement if the idea contained therein can
   be expressed in only one way.


    >>> print(oracle.holdings[12])
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <Google> infringed the copyright on <the
          Java API>
        GIVEN:
          the Fact that <the Java API> was essentially the only way to express
          the idea that it embodied
        DESPITE:
          the Fact that <the Java API> was copyrightable
        GIVEN the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)
        DESPITE the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)

    >>> print(oracle.holdings[13])
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact that <Google> infringed the copyright on <the Java API>
        GIVEN:
          the Fact that <the Java API> was copyrightable
          absence of the Fact that <the Java API> was essentially the only way
          to express the idea that it embodied
          absence of the Fact that <the Java API> was a scene a faire
        GIVEN the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)
        DESPITE the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


A Missing Holding
^^^^^^^^^^^^^^^^^

The following text represents a rule posited by the Oracle court, but
it’s not currently possible to create a corresponding Holding object,
because AuthoritySpoke doesn’t yet include “Argument” objects.

   Google responds that Oracle waived its right to assert
   copyrightability based on the 7,000 lines of declaring code by
   failing “to object to instructions and a verdict form that
   effectively eliminated that theory from the case.” Appellee Br. 67…We
   find that Oracle did not waive arguments based on Google’s literal
   copying of the declaring code.

   Regardless of when the analysis occurs, we conclude that merger does
   not apply on the record before us…We have recognized, however,
   applying Ninth Circuit law, that the “unique arrangement of computer
   program expression … does not merge with the process so long as
   alternate expressions are available.”…The evidence showed that Oracle
   had “unlimited options as to the selection and arrangement of the
   7000 lines Google copied.”…This was not a situation where Oracle was
   selecting among preordained names and phrases to create its packages.

    >>> print(oracle.holdings[14])
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact it is false that <the Java API> was essentially the only way
          to express the idea that it embodied
        GIVEN:
          the Fact that <Sun Microsystems> created <the Java API>
          the Fact that when creating <the Java API>, <Sun Microsystems> could
          have selected and arranged its names and phrases in unlimited
          different ways
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
        DESPITE the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)


   the relevant question for copyright-ability purposes is not whether
   the work at issue contains short phrases — as literary works often do
   — but, rather, whether those phrases are creative.

    >>> print(oracle.holdings[15])
    the Holding to ACCEPT
      the Rule that the court MUST SOMETIMES impose the
        RESULT:
          the Fact that <the Java API> was copyrightable
        GIVEN:
          the Fact that <the Java API> was a literary work
          the Fact that the short phrases in <the Java API> was creative
        DESPITE:
          the Fact that <the Java API> contained short phrases
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
        DESPITE the ENACTMENTS:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)
          "The following are examples of works not subject to copyright and applications for registration of such works cannot be entertained: Words and short phrases such as names, titles, and slogans; familiar symbols or designs; mere variations of typographic ornamentation, lettering or coloring; mere listing of ingredients or contents; Ideas, plans, methods, systems, or devices, as distinguished from the particular manner in which they are expressed or described in a writing;  Blank forms, such as time cards, graph paper, account books, diaries, bank checks, scorecards, address books, report forms, order forms and the like, which are designed for recording information and do not in themselves convey information; Works consisting entirely of information that is common property containing no original authorship, such as, for example: Standard calendars, height and weight charts, tape measures and rulers, schedules of sporting events, and lists or tables taken from public documents or other common sources. Typeface as typeface." (/us/cfr/t37/s202.1 1992-02-21)


   In the computer context, “the scene a faire doctrine denies
   protection to program elements that are dictated by external factors
   such as ‘the mechanical specifications of the computer on which a
   particular program is intended to run’ or ‘widely accepted
   programming practices within the computer industry. Like merger, the
   focus of the scenes a faire doctrine is on the circumstances
   presented to the creator, not the copier.

    >>> print(oracle.holdings[16])
    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <the Java API> was a scene a faire
        GIVEN:
          the Fact that <the Java language> was a computer program
          the Fact that <the Java API> was an element of <the Java language>
          the Fact that the creation of <the Java API> was dictated by external
          factors such as the mechanical specifications of the computer on which
          <the Java language> was intended to run or widely accepted programming
          practices within the computer industry
        GIVEN the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)
        DESPITE the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)


   Specifically, we find that Lotus is inconsistent with Ninth Circuit
   case law recognizing that the structure, sequence, and organization
   of a computer program is eligible for copyright protection where it
   qualifies as an expression of an idea, rather than the idea itself.

    >>> print(oracle.holdings[17])
    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <the Java API> was copyrightable
        GIVEN:
          the Fact that <the Java language> was a computer program
          the Fact that <the Java API> was the structure, sequence, and
          organization of <the Java language>
          the Fact that <the Java API> was the expression of an idea
          the Fact it is false that <the Java API> was an idea
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
        DESPITE the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)


   an original work — even one that serves a function — is entitled to
   copyright protection as long as the author had multiple ways to
   express the underlying idea. Section 102(b) does not, as Google seems
   to suggest, automatically deny copyright protection to elements of a
   computer program that are functional.

    >>> print(oracle.holdings[18])
    the Holding to ACCEPT
      the Rule that the court MUST ALWAYS impose the
        RESULT:
          the Fact that <the Java API> was copyrightable
        GIVEN:
          the Fact that <the Java API> was an original work
          the Fact that <Sun Microsystems> was the author of <the Java API>
          the Fact that when creating <the Java API>, <Sun Microsystems> had
          multiple ways to express its underlying idea
        DESPITE:
          the Fact that <the Java API> served a function
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
        DESPITE the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)


   Until either the Supreme Court or Congress tells us otherwise, we are
   bound to respect the Ninth Circuit’s decision to afford software
   programs protection under the copyright laws. We thus decline any
   invitation to declare that protection of software programs should be
   the domain of patent law, and only patent law.

    >>> print(oracle.holdings[19])
    the Holding to ACCEPT
      the Rule that the court MAY SOMETIMES impose the
        RESULT:
          the Fact that <the Java language> was copyrightable
        GIVEN:
          the Fact that <the Java language> was a computer program
        GIVEN the ENACTMENT:
          "Copyright protection subsists, in accordance with this title, in original works of authorship fixed in any tangible medium of expression, now known or later developed, from which they can be perceived, reproduced, or otherwise communicated, either directly or with the aid of a machine or device.…" (/us/usc/t17/s102/a 2013-07-18)
        DESPITE the ENACTMENT:
          "In no case does copyright protection for an original work of authorship extend to any idea, procedure, process, system, method of operation, concept, principle, or discovery, regardless of the form in which it is described, explained, illustrated, or embodied in such work." (/us/usc/t17/s102/b 2013-07-18)

