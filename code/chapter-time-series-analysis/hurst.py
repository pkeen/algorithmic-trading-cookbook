import pandas as pd

from numpy import cumsum, log, polyfit, sqrt, std, subtract
from numpy.random import randn

def create_dataframe(data_csv):
    """
    Pricing data csv download for Google (GOOG)
    OHLCV data from 01/09/2004-31/08/2020 into a DataFrame.
        
    Parameters
    ----------
    data_csv : `csv`
    CSV file containing pricing data

    Returns
    -------
    `pd.DataFrame`
    A DataFrame containing Google (GOOG) OHLCV data from
    01/09/2004-31/08/2020. Index is a Datetime object.

    """
    # Create a pandas DataFrame containing the Google OHLCV data
    goog = pd.read_csv(data_csv, index_col="Date")
    # Convert index to a Datetime object
    goog.index = pd.to_datetime(goog.index)
    return goog


def hurst(ts):
    """
    Returns the Hurst Exponent of the time series vector ts

    Parameters
    ----------
    ts : `numpy.array`
        Time series upon which the Hurst Exponent will be calculated

    Returns
    -------
    'float'
        The Hurst Exponent from the poly fit output
    """
    # Create the range of lag values
    lags = range(2, 100)

    # Calculate the array of the variances of the lagged differences
    tau = [sqrt(std(subtract(ts[lag:], ts[:-lag]))) for lag in lags]

    # Use a linear fit to estimate the Hurst Exponent
    poly = polyfit(log(lags), log(tau), 1)

    # Return the Hurst exponent from the polyfit output
    return poly[0]*2.0


def gbm():
    """
    Returns a Geometric Brownian Motion Series with Randon seed set to 42

    Parameters
    ----------
    None

    Returns
    -------
    `np.array`
        Geometric Brownian Motion Series
    """
    return log(cumsum(randn(100000))+1000)


def mr():
    """
    Returns a Mean Reverting Series with Randon seed set to 42

    Parameters
    ----------
    None

    Returns
    -------
    `np.array`
        Mean Reverting Series
    """
    return log(randn(100000)+1000)


def tr():
    """
    Returns a Trending Series with Randon seed set to 42

    Parameters
    ----------
    None

    Returns
    -------
    `np.array`
        Mean Trending Series
    """
    return log(cumsum(randn(100000)+1)+1000)


def generate_hurst(gbm, mr, tr, goog_df):
    """
    Generates the Hurst Exponent for all time series.

    Parameters
    ----------
    gbm : `np.array`
        Geometric Brownian Motion Series
    mr : `np.array`
        Mean Reverting Series
    tr : `np.array`
        Mean Trending Series
    goog_df : `pd.DataFrame`
        A DataFrame containing Google (GOOG) OHLCV data from
        01/09/2004-31/08/2020. Index is a Datetime object.

    Returns
    -------
    None
    """
    series = [gbm, mr, tr, goog_df['Adj Close'].values]
    names = ['GBM', 'MR', 'TR', 'GOOG']
    [
        print(f'Hurst({names[i]}): {hurst(ser)}') 
        for i, ser in enumerate(series)
    ]


if __name__ == "__main__":
    data_csv = "PATH/To/Your/GOOG.csv"
    goog_df = create_dataframe(data_csv)
    gbm_series = gbm()
    mr_series = mr()
    tr_series = tr()
    generate_hurst(gbm_series, mr_series, tr_series, goog_df)
