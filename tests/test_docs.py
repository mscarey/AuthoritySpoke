from authorityspoke import Holding
from authorityspoke.examples import beard_act


class TestStatuteDocs:
    """
    Replicating this test from the statute rules guide:

    >>> beard_holdings = [Holding(rule=rule) for rule in beard_act.rules()]
    >>> chin_rule = beard_holdings[0].rule
    >>> longer_hair = [beard_holdings[0].model_copy(deep=True)]
    >>> longer_hair[0].rule.inputs[1].predicate.quantity_range.sign = "=="
    >>> longer_hair[0].rule.inputs[1].predicate.quantity_range.quantity_magnitude = 8
    >>> print(longer_hair[0])
    the Holding to ACCEPT
      the Rule that the court MAY ALWAYS impose the
        RESULT:
          the fact that <the suspected beard> was a beard
        GIVEN:
          the fact that <the suspected beard> was facial hair
          the fact that the length of <the suspected beard> was exactly equal to
          8 millimeter
          the fact that <the suspected beard> occurred on or below the chin
        GIVEN the ENACTMENT:
          "In this Act, beard means any facial hair no shorter than 5 millimetres in length that: occurs on or below the chin…" (/test/acts/47/4 1935-04-01)
    >>> chin_rule.implies(longer_hair[0])
    True
    """

    def test_rules_comparing_distance(self):
        """
        Illustrate that a rule about "hair no shorter than 5 millimetres" implies a rule about hair that is exactly 8 millimetres.
        """
        beard_holdings = [Holding(rule=rule) for rule in beard_act.rules()]
        longer_hair = [beard_holdings[0].model_copy(deep=True)]
        longer_hair[0].rule.inputs[1].predicate.quantity_range.sign = "=="
        longer_hair[0].rule.inputs[1].predicate.quantity_range.quantity_magnitude = 8
        chin_rule = beard_holdings[0].rule
        assert chin_rule.implies(longer_hair[0])
