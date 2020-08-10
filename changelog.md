Changelog
=========
dev
-----------
- Create `ComparableGroup` class for unordered collections of `Factor`s
- Create `FactorSequence` class for ordered collections of `Factor`s
- Eliminate Analogy class, moving its methods to `FactorGroup` and `FactorSequence`
- Add `Factor.consistent_with` method to search for available context causing two `Factor`s not to contradict
- Add "or" operator for `FactorGroup`s
- Integrate Legislice API client for retrieving text from US Constitution and US Code
- Remove functions for loading legislation text from XML files. Use API client instead.
- Delete classes for accessing XML legislation files: `Code`, `Regime`, and `Jurisdiction`

0.3.4 (2020-01-02)
------------------
- Create broader conditions for Procedure.contradicts()

0.3.3 (2020-01-01)
------------------
- Add `__init__.py` to utils folder

0.3.2 (2020-01-01)
------------------
- Publish repo's utils folder as part of AuthoritySpoke package

0.3.1 (2020-01-01)
------------------
- Fix bug where some types of cross-references caused loading of Holdings from JSON to fail
- Update case download function because Case Access Project API no longer includes "casebody" field in all responses from cases endpoint
- `new_context` function can use string to find Factor to be replaced
- Enactment URIs can target a chapeau or continuation
- Fix bug that created [multiple pint Unit Registries](https://github.com/hgrecco/pint/issues/581)

0.3.0 (2019-12-07)
------------------
- Enactments may choose text by section without a TextQuoteSelector
- Remove "regime" parameter from Enactment
- Add data serialization using [Marshmallow](https://marshmallow.readthedocs.io/)
- Migrate JSON data loading functions to Marshmallow
- Add Decision class containing Opinions
- Add Explanation class to clarify relationships between Holdings
- Improve readability of string representations of objects
- Move text selectors to separate [anchorpoint](https://anchorpoint.readthedocs.io/) library
- Add [apispec](https://github.com/marshmallow-code/apispec) schema specification for Holding input JSON files

0.2.0 (2019-09-24)
------------------

- Merge ProceduralRule class with Rule
- Split aspects of Rule into a separate Holding class
- Use Selectors to anchor Holdings to Opinion text
- Ignore was/were differences in Predicate content text
- Let input JSON label a Rule as the "exclusive" way to get output
- Create addition operator for Factors, Rules, and Holdings
- Let Rule init method handle the necessary Procedure init method
- Use addition operator to add Factors as Rule inputs
- Use addition operator to add Enactments to Rules
- Create function to consolidate list of Enactments
- Add Union operator for Rules and Holdings
- Move functions for loading objects from JSON and XML to new I/O modules
- Add "explain" functions to show how generic Factors match up when a contradiction or implication exists
- Add whitespace to `__str__` methods for greater clarity

0.1.0 (2019-06-10)
------------------

- Add Regime and Jurisdiction classes to organize Enactments
- Add TextQuoteSelector class to select text from Enactments
- Change Enactment init method to use TextQuoteSelectors
