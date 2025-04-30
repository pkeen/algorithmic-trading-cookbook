from datetime import datetime as dt

import numpy as np

from backtest import Backtest
from data import HistoricCSVDataHandler
from event import SignalEvent
from execution import SimulatedExecutionHandler
from portfolio import Portfolio
from strategy import Strategy


class BuyAndHoldStrategy(Strategy):
    """
    This is an extremely simple strategy that goes LONG all of the 
    symbols as soon as a bar is received. It will never exit a position.

    It is primarily used as a testing mechanism for the Strategy class
    as well as a benchmark upon which to compare other strategies.
    """

    def __init__(self, bars, events):
        """
        Initialises the buy and hold strategy.

        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events

        # Once buy & hold signal is given, these are set to True
        self.bought = self._calculate_initial_bought()

        # strategy.py

    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to False.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = False
        return bought

    def calculate_signals(self, event):
        """
        For "Buy and Hold" we generate a single signal per symbol
        and then no additional signals. This means we are 
        constantly long the market from the date of strategy
        initialisation.

        Parameters
        event - A MarketEvent object. 
        """
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars(s, N=1)
                if bars is not None and bars != []:
                    if self.bought[s] == False:
                        # (Strategy ID, Symbol, Datetime, Type = LONG, SHORT or EXIT, Strength)
                        signal = SignalEvent(1, s, bars[0][0], 'LONG', 1.0)
                        self.events.put(signal)
                        self.bought[s] = True

         
if __name__ == "__main__":
    csv_dir = "/path/to/your/csv/file"
    symbol_list = ['AAPL']
    initial_capital = 100000.0
    start_date = dt(1999,11,12,0,0,0)
    heartbeat = 0.0

    backtest = Backtest(csv_dir, 
                        symbol_list, 
                        initial_capital, 
                        heartbeat,
                        start_date,
                        HistoricCSVDataHandler, 
                        SimulatedExecutionHandler, 
                        Portfolio, 
                        BuyAndHoldStrategy)
    
    backtest.simulate_trading()
