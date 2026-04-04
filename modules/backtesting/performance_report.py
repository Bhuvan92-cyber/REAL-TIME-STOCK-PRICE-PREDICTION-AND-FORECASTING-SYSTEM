import numpy as np


class PerformanceReport:
    """
    Generates performance metrics from backtest results.
    """

    def __init__(self, portfolio_df):

        self.df = portfolio_df

    def generate(self):

        returns = self.df["portfolio_value"].pct_change().dropna()

        total_return = (
            self.df["portfolio_value"].iloc[-1]
            - self.df["portfolio_value"].iloc[0]
        ) / self.df["portfolio_value"].iloc[0]

        sharpe_ratio = self.calculate_sharpe(returns)

        max_drawdown = self.calculate_drawdown()

        return {
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown
        }

    def calculate_sharpe(self, returns, risk_free_rate=0):

        excess_returns = returns - risk_free_rate

        if excess_returns.std() == 0:
            return 0

        sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()

        return sharpe

    def calculate_drawdown(self):

        cumulative = self.df["portfolio_value"]

        running_max = cumulative.cummax()

        drawdown = (cumulative - running_max) / running_max

        return drawdown.min()