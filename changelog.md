Changelog
=========

dev
---

- Merge ProceduralRule class with Rule
- Ignore was/were differences in Predicate content text
- Let input JSON label a Rule as the "exclusive" way to get output
- Create addition operator for Factors and Rules
- Let Rule init method handle the necessary Procedure init method
- Use addition operator to add Factors as Rule inputs
- Use addition operator to add Enactments to Rules
- Create function to consolidate list of Enactments

0.1.0 (2019-06-10)
------------------

- Add Regime and Jurisdiction classes to organize Enactments
- Add TextQuoteSelector class to select text from Enactments
- Change Enactment init method to use TextQuoteSelectors
