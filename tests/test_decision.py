class TestDecision:
    def test_decision_string(self, make_decision):
        decision = make_decision["cardenas"]
        assert str(decision) == "People v. Cardenas, 31 Cal. 3d 897 (1982-07-08)"

    def test_posit_holdings(self, make_decision, make_holding):
        """
        "Positing" Holdings causes the Holdings to be assigned to the Decision's
        majority Opinion.
        """

        watt = make_decision["watt"]
        watt.posit([make_holding["h1"], make_holding["h2"]])
        assert watt.majority.holdings[-1] == make_holding["h2"]
