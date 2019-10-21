Changelog
=========

Dev
------------------
- Enactments may choose text by section without a TextQuoteSelector
- Remove "regime" parameter from Enactment
- Add data serialization using Marshmallow
- Migrate JSON data loading functions to Marshmallow
- Add Decision class containing Opinions

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
