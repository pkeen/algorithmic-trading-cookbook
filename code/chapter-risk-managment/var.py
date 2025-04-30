# var.py

import numpy as np
import pandas as pd
from scipy.stats import norm


def create_dataframe(csv):
    """
    Read pricing data CSV download for C 
    OHLCV data from 01/01/2010-01/01/2014 into a DataFrame.

    Parameters
   -----------
   csv : `csv`
       CSV file containing pricing data.
    
    Returns
    -------
    ts : `pd.DataFrame`
        A DataFrame containing C OHLCV data from
        01/01/2010-01/01/2014. Index is a DateTime object.  
   """
    # obtain stock information
    ts = pd.read_csv(csv)
    ts = ts.set_index(pd.DatetimeIndex(ts['Date']))
    return ts


def create_returns_series(ts):
    """
    Create Returns series from OHLCV DataFrame.

    Parameters
    ----------
    ts : `pd.DataFrame`
        A DataFrame containing C OHLCV data from
        01/01/2010-01/01/2014. Index is a DateTime object.

    Returns
    -------
    ts : `pd.DataFrame
        A DateFrame with OHCLV data and a Returns series.
    """
    # Calculate the percentage change
    ts["rets"] = ts["Adj Close"].pct_change()
    return ts


def _var_cov_var(P, c, mu, sigma):
    """
    Variance-Covariance calculation of daily Value-at-Risk
    using confidence level c, with mean of returns mu
    and standard deviation of returns sigma, on a portfolio
    of value P.

    Parameters
    ----------
    P : `int`
        Portfolio Value.
    c : `float`
        Confidence Level.
    mu : `float`
        Mean of Returns Series.
    sigma : `float`
        Standard Deviation of Returns Series.

    Returns
    -------
    `float`
        Variance-Covariance measure.
    """
    alpha = norm.ppf(1-c, mu, sigma)
    return P - P*(alpha + 1)


def var(rets):
    """
    Parameters for Variance-Covariance calculation.

    Parameters
    ----------
    rets : `pd.DataFrame`
        OHLCV DataFrame with Returns Series.

    Returns
    -------
    'float'
        Variance-Covariance measure.
    """
    P = 1e6   # 1,000,000 USD
    c = 0.99  # 99% confidence interval
    mu = np.mean(rets["rets"])
    sigma = np.std(rets["rets"])
    return _var_cov_var(P, c, mu, sigma)


if __name__ == "__main__":
    # CSV file of OHLCV data for C from 1/1/2010 to 1/1/2014
    csv = "PATH/TO/YOUR/CSV"
    
    citi = create_dataframe(csv)
    rets = create_returns_series(citi)
    var = var(rets) 
    
    print(f"Value-at-Risk: ${var:0.2f}")
