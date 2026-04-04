import pandas as pd
from modules.backtesting.portfolio_simulator import PortfolioSimulator
from modules.backtesting.transaction_cost_model import TransactionCostModel
from modules.backtesting.performance_report import PerformanceReport


class StrategyBacktester:
    """
    Runs trading strategy on historical data using signals.
    """

    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.transaction_model = TransactionCostModel()
        self.portfolio = PortfolioSimulator(initial_capital)

    def run_backtest(self, df: pd.DataFrame):
        """
        Executes the backtest loop.
        """

        for index, row in df.iterrows():

            price = row["close"]
            signal = row["signal"]

            cost = self.transaction_model.calculate_cost(price)

            if signal == 1:
                self.portfolio.buy(price, cost)

            elif signal == -1:
                self.portfolio.sell(price, cost)

            self.portfolio.update_portfolio_value(price)

        results = self.portfolio.get_portfolio_history()

        report = PerformanceReport(results)

        return report.generate()