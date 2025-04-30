# sharpe.py

import numpy as np
import pandas as pd


def create_stock_df(csv):
    """
    Create DataFrame from CSV file with Date as DatetimeIndex.

    Parameters
    ----------
    csv: `csv`
        A csv file containing OHLCV data, with columns of the following 
        format: Date,Open,High,Low,Close,Adj Close,Volume.
    Returns
    -------
    csv_df: `pd.DataFrame`
        A DataFrame of OHCLV data with Date as Index.
    """
    csv_df = pd.read_csv(csv)
    csv_df = csv_df.set_index(pd.DatetimeIndex(csv_df['Date']))
    return csv_df


def _annualised_sharpe(returns, N=252):
    """
    Calculate the annualised Sharpe ratio of a returns stream
    based on a number of trading periods, N. N defaults to 252,
    which then assumes a stream of daily returns.

    The function assumes that the returns are the excess of
    those compared to a benchmark.

    Parameters
    ----------
    returns : `pd.Series`
        A Pandas Series containing the daily returns of an equity
        ticker symbol.
    N : `int`
        Default 252. The number of trading periods in the reurns series.

    Returns
    -------
    `float`
        Annualised Sharpe for the returns series. 
    """
    return np.sqrt(N) * returns.mean() / returns.std()


def equity_sharpe(ticker):
    """
    Calculates the annualised Sharpe ratio based on the daily
    returns of an equity ticker symbol.
    
    Paramters
    ---------
    ticker: `pd,DataFrame`
        DataFrame of OHCLV data created by create_stock_df.

    Returns
    -------
    `float`
        Annualised Sharpe for daily returns in execss of risk-free rate
    """
    # Use the percentage change method to easily calculate daily returns
    ticker['daily_ret'] = ticker['Adj Close'].pct_change()

    # Assume an average annual risk-free rate over the period of 5%
    ticker['excess_daily_ret'] = ticker['daily_ret'] - 0.05/252

    # Return the annualised Sharpe ratio based on the excess daily returns
    return _annualised_sharpe(ticker['excess_daily_ret'])


def market_neutral_sharpe(ticker, benchmark):
    """
    Calculates the annualised Sharpe ratio of a market
    neutral long/short strategy inolving the long of 'ticker'
    with a corresponding short of the 'benchmark'.
    
    Paramters
    ---------
    ticker: `pd.DataFrame`
        DataFrame of OHCLV data created by create_stock_df.
    benchmark: `pd.DataFrame`
        DataFrame of benchmark OHCLV data created by create_stock_df.
       
    Returns
    -------
    `float`
        Market neutral annualised Sharpe ratio.
    """
    # Calculate the percentage returns on each of the time series
    ticker['daily_ret'] = ticker['Adj Close'].pct_change()
    benchmark['daily_ret'] = benchmark['Adj Close'].pct_change()

    # Create a new DataFrame to store the strategy information
    # The net returns are (long - short)/2, since there is twice
    # the trading capital for this strategy
    strat = pd.DataFrame(index=ticker.index)
    strat['net_ret'] = (ticker['daily_ret'] - benchmark['daily_ret'])/2.0

    # Return the annualised Sharpe ratio for this strategy
    return _annualised_sharpe(strat['net_ret'])


if __name__ == "__main__":
    goog_csv = "PATH/TO/YOUR/GOOGL/CSV"
    spy_csv = "PATH/TO/YOUR/SPY/CSV"

    goog = create_stock_df(goog_csv)
    benchmark = create_stock_df(spy_csv)
    
    print(f"GOOGL Sharpe Ratio: {equity_sharpe(goog)}")
    print(
        f"""Market Neutral Sharpe Ratio: 
        {market_neutral_sharpe(goog, benchmark)}"""
    )
