# intraday_mr.py

from datetime import datetime as dt
from itertools import product

import pandas as pd
import statsmodels.api as sm

from strategy import Strategy
from event import SignalEvent
from backtest import Backtest
from hft_data import HistoricCSVDataHandlerHFT
from hft_portfolio import PortfolioHFT
from execution import SimulatedExecutionHandler


class IntradayOLSMRStrategy(Strategy):
    """
    Uses ordinary least squares (OLS) to perform a rolling linear
    regression to determine the hedge ratio between a pair of equities.
    The z-score of the residuals time series is then calculated in a
    rolling fashion and if it exceeds an interval of thresholds
    (defaulting to [0.5, 3.0]) then a long/short signal pair are generated
    (for the high threshold) or an exit signal pair are generated (for the
    low threshold).
    """
    
    def __init__(
        self, bars, events, ols_win=100, 
        z_low=0.5, z_high=3.0
    ):
        """
        Initialises the stat arb strategy.

        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.ols_win = ols_win
        self.z_low = z_low
        self.z_high = z_high

        self.pair = tuple(self.symbol_list)
        self.datetime = dt.utcnow()

        self.long_market = False
        self.short_market = False

    def calculate_xy_signals(self, zscore_last):
        """
        Calculates the actual x, y signal pairings
        to be sent to the signal generator.

        Parameters
        zscore_last - The current zscore to test against
        """
        y_signal = None
        x_signal = None
        p0 = self.pair[0]
        p1 = self.pair[1]
        cur_dt = self.datetime
        hr = abs(self.hedge_ratio)

        # If we're long the market and below the 
        # negative of the high zscore threshold
        if zscore_last <= -self.z_high and not self.long_market:
            self.long_market = True
            y_signal = SignalEvent(1, p0, cur_dt, 'LONG', 1.0)
            x_signal = SignalEvent(1, p1, cur_dt, 'SHORT', hr)

        # If we're long the market and between the
        # absolute value of the low zscore threshold
        if abs(zscore_last) <= self.z_low and self.long_market:
            self.long_market = False
            y_signal = SignalEvent(1, p0, cur_dt, 'EXIT', 1.0)
            x_signal = SignalEvent(1, p1, cur_dt, 'EXIT', 1.0)

        # If we're short the market and above  
        # the high zscore threshold
        if zscore_last >= self.z_high and not self.short_market:
            self.short_market = True
            y_signal = SignalEvent(1, p0, cur_dt, 'SHORT', 1.0)
            x_signal = SignalEvent(1, p1, cur_dt, 'LONG', hr)

        # If we're short the market and between the
        # absolute value of the low zscore threshold
        if abs(zscore_last) <= self.z_low and self.short_market:
            self.short_market = False
            y_signal = SignalEvent(1, p0, cur_dt, 'EXIT', 1.0)
            x_signal = SignalEvent(1, p1, cur_dt, 'EXIT', 1.0)

        return y_signal, x_signal

    def calculate_signals_for_pairs(self):
        """
        Generates a new set of signals based on the mean reversion
        strategy.

        Calculates the hedge ratio between the pair of tickers. 
        We use OLS for this, although we should ideally use CADF.
        """
        # Obtain the latest window of values for each 
        # component of the pair of tickers
        y = self.bars.get_latest_bars_values(
            self.pair[0], "close", N=self.ols_win
        )
        x = self.bars.get_latest_bars_values(
            self.pair[1], "close", N=self.ols_win
        )
        #x = sm.add_constant(x)

        if y is not None and x is not None:
            # Check that all window periods are available
            if len(y) >= self.ols_win and len(x) >= self.ols_win:
                # Calculate the current hedge ratio using  OLS
                self.hedge_ratio = sm.OLS(y, x).fit().params[0]

                # Calculate the current z-score of the residuals
                spread = y - self.hedge_ratio * x
                zscore_last = ((spread - spread.mean())/spread.std())[-1]

                # Calculate signals and add to events queue
                y_signal, x_signal = self.calculate_xy_signals(zscore_last)
                if y_signal is not None and x_signal is not None:
                    self.events.put(y_signal)
                    self.events.put(x_signal)

    def calculate_signals(self, event):
        """
        Calculate the SignalEvents based on market data.
        """
        if event.type == 'MARKET':
            self.calculate_signals_for_pairs()


if __name__ == "__main__":
    csv_dir = '/path/to/your/csv/file'  # CHANGE THIS!
    symbol_list = ['USO', 'XOM']
    initial_capital = 100000.0
    heartbeat = 0.0
    start_date = dt(2022, 1, 10, 12, 19, 0)

    # Create the strategy parameter grid
    # using the itertools cartesian product generator
    strat_lookback = [50, 100, 200]
    strat_z_entry = [2.0, 2.5, 3.0]
    strat_z_exit = [0.5, 1.0, 1.5]
    strat_params_list = list(product(
        strat_lookback, strat_z_entry, strat_z_exit
    ))

    # Create a list of dictionaries with the correct
    # keyword/value pairs for the strategy parameters
    strat_params_dict_list = [
        dict(ols_win=sp[0], z_high=sp[1], z_low=sp[2])
        for sp in strat_params_list
    ]

    performance = {
        'ols_win': [],
        'z_high': [],
        'z_low': [],
        'Total Return': [],
        'Sharpe': [],
        'Max Drawdown': [],
        'Drawdown Duration': []
     }
    for strat_params_dict in strat_params_dict_list:
        backtest = Backtest(
            csv_dir, symbol_list, initial_capital, heartbeat, 
            start_date, HistoricCSVDataHandlerHFT, SimulatedExecutionHandler, 
            PortfolioHFT, IntradayOLSMRStrategy, 
            strat_params_dict=strat_params_dict
        )
        tot_ret, sharpe, max_dd, dd_dur = backtest.simulate_trading()
        for key, value in strat_params_dict.items():
            performance[key].append(value)
        performance['Total Return'].append(tot_ret)
        performance['Sharpe'].append(sharpe)
        performance['Max Drawdown'].append(max_dd)
        performance['Drawdown Duration'].append(dd_dur)
    perf_df = pd.DataFrame(performance)
    perf_df.to_csv('output.csv')
    print(perf_df)
