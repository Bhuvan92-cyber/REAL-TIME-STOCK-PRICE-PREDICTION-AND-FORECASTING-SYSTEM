import pandas as pd


class PortfolioSimulator:
    """
    Simulates portfolio value over time.
    """

    def __init__(self, initial_capital):

        self.cash = initial_capital
        self.shares = 0

        self.history = []

    def buy(self, price, cost):

        if self.cash > price:

            shares_to_buy = int(self.cash / price)

            total_price = shares_to_buy * price + cost

            self.cash -= total_price
            self.shares += shares_to_buy

    def sell(self, price, cost):

        if self.shares > 0:

            total_sale = self.shares * price - cost

            self.cash += total_sale
            self.shares = 0

    def update_portfolio_value(self, price):

        value = self.cash + (self.shares * price)

        self.history.append({
            "cash": self.cash,
            "shares": self.shares,
            "price": price,
            "portfolio_value": value
        })

    def get_portfolio_history(self):

        return pd.DataFrame(self.history)