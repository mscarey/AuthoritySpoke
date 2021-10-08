Changelog
=========
dev
------------------
* remove marshmallow and marshmallow-oneofschema
* remove apispec and apispec-oneofschema
* replace marshmallow and apispec with pydantic

0.8.1 (2021-09-18)
------------------
* limit version range for Legislice import

0.8.0 (2021-08-12)
------------------
* import Opinion, Decision, and Court data classes from Justopinion package
* depend on Justopinion package to download caselaw with CAPClient class
* Holdings of an Opinion are now stored on an OpinionReading, not on the Opinion
* read_decision function now makes a DecisionReading, not a Decision
* install with setup.py, not setup.cfg
* fix error in Opinion.explain_contradiction(HoldingGroup)

0.7.2 (2021-06-16)
------------------
* accept added fields in CAPCitation schema
* change method for FakeEnactment finding file

0.7.1 (2021-06-15)
------------------
* change "quotes" schema field names to "anchors"
* add doctests to documentation
* update example in readme to work with current version
* use new Eyecite API changing "base_citation" to "corrected_citation"

0.7.0 (2021-05-20)
------------------
* remove Enactment download functions (use Legislice download client instead)
* remove Opinion download functions (use CAPClient class instead)
* use different Legislice schema imports for JSON and YAML
* move fake download client to separate module
* add read methods to CAP opinion download client
* add read methods to CAPClient
* DecisionSchema can accept months instead of dates
* merge CAPCitation and CAPCitationTo schemas
* Holding has separate add_enactment and with_enactment methods
* Rule has separate add_enactment and with_enactment methods
* Rule has separate add_factor and with_factor methods
* Procedure has separate add_factor and with_factor methods
* increase versions of Nettlesome and Legislice dependencies
* add CAPClient to top level of package
* add "Creating and Loading Holding Data" documentation page
* Rules select all text of Enactments without selected text only during init, not during schema load
* change field name from "quotes" to "anchors" in YAML import files
* fix bug: dump methods couldn't find Decision and Opinion schemas

0.6.0 (2021-04-09)
------------------
* Comparison methods use Explanations instead of ContextRegisters
* Remove io/anchors module
* Remove "factors" module that conflicted with Nettlesome module of same name
* Add Fact.negated method
* Remove "role" param for Procedure.add_factor
* Rules can be added even if one of the operands has more Enactments
* Procedure.recursive_terms doesn't include FactorGroups
* Procedure.terms doesn't include FactorGroups
* Add comparable_with methods
* Decision is no longer a dataclass
* remove context param from Opinion comparisons
* handle Opinion.explanations_implication(HoldingGroup)
* Increase minimum Nettlesome version to 0.5.0

0.5.1 (2021-03-08)
------------------
* Import Nettlesome library as dependency
* Remove "anchors" fields from Factors in AuthoritySpoke Holding API Schema

0.5.0 (2021-01-25)
------------------
* Predicate.content attribute no longer includes an extra placeholder for a "quantity"
* Predicate.content attribute must be a valid Python string template
* Rename "context_factors" field to "terms"
* Rely on Predicate placeholder names to label terms as interchangeable
* Remove Predicate.reciprocal field used to label terms as interchangeable
* Add Comparable class for Predicate with a numeric comparison
* Rename Comparable.quantity to Comparable.expression
* Comparable.expression can be a datetime.date

0.4.1 (2021-01-02)
------------------
* Increase minimum Legislice version to 0.4.1
* Remove `read_enactments` and `read_enactment`. Use Legislice's download client or schema instead.

0.4.0 (2020-08-26)
------------------
* Create `ComparableGroup` class for unordered `Factor` collections
* Create `FactorSequence` class for ordered `Factor` collections
* Eliminate Analogy class, moving its methods to `FactorGroup` and `FactorSequence`
* Add `Factor.consistent_with` method to search for available context avoiding contradiction
* Add "or" operator for `FactorGroup`
* Integrate Legislice API client for retrieving text from US Constitution and US Code
* Remove functions for loading legislation text from XML files. Use API client instead.
* Delete classes for accessing XML legislation files: `Code`, `Regime`, and `Jurisdiction`

0.3.4 (2020-01-02)
------------------
* Create broader conditions for Procedure.contradicts()

0.3.3 (2020-01-01)
------------------
* Add `__init__.py` to utils folder

0.3.2 (2020-01-01)
------------------
* Publish repo's utils folder as part of AuthoritySpoke package

0.3.1 (2020-01-01)
------------------
* Fix bug where some types of cross-references caused loading of Holdings from JSON to fail
* Update case download function because Case Access Project API no longer includes "casebody" field in all responses from cases endpoint
* `new_context` function can use string to find Factor to be replaced
* Enactment URIs can target a chapeau or continuation
* Fix bug that created [multiple pint Unit Registries](https://github.com/hgrecco/pint/issues/581)

0.3.0 (2019-12-07)
------------------
* Enactments may choose text by section without a TextQuoteSelector
* Remove "regime" parameter from Enactment
* Add data serialization using [Marshmallow](https://marshmallow.readthedocs.io/)
* Migrate JSON data loading functions to Marshmallow
* Add Decision class containing Opinions
* Add Explanation class to clarify relationships between Holdings
* Improve readability of string representations of objects
* Move text selectors to separate [anchorpoint](https://anchorpoint.readthedocs.io/) library
* Add [apispec](https://github.com/marshmallow-code/apispec) schema specification for Holding input JSON files

0.2.0 (2019-09-24)
------------------

* Merge ProceduralRule class with Rule
* Split aspects of Rule into a separate Holding class
* Use Selectors to anchor Holdings to Opinion text
* Ignore was/were differences in Predicate content text
* Let input JSON label a Rule as the "exclusive" way to get output
* Create addition operator for Factors, Rules, and Holdings
* Let Rule init method handle the necessary Procedure init method
* Use addition operator to add Factors as Rule inputs
* Use addition operator to add Enactments to Rules
* Create function to consolidate list of Enactments
* Add Union operator for Rules and Holdings
* Move functions for loading objects from JSON and XML to new I/O modules
* Add "explain" functions to show how generic Factors match up when a contradiction or implication exists
* Add whitespace to `__str__` methods for greater clarity

0.1.0 (2019-06-10)
------------------

* Add Regime and Jurisdiction classes to organize Enactments
* Add TextQuoteSelector class to select text from Enactments
* Change Enactment init method to use TextQuoteSelectors