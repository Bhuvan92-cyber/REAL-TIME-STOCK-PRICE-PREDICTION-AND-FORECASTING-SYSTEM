class TransactionCostModel:
    """
    Models transaction costs like brokerage and slippage.
    """

    def __init__(self,
                 brokerage_rate=0.001,
                 slippage_rate=0.0005):

        self.brokerage_rate = brokerage_rate
        self.slippage_rate = slippage_rate

    def calculate_cost(self, price):

        brokerage = price * self.brokerage_rate
        slippage = price * self.slippage_rate

        return brokerage + slippage