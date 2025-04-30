# adf.py
import pandas as pd
import statsmodels.tsa.stattools as ts

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


def augmented_dickey_fuller(goog):
    """
    Carry out the Augmented Dickey-Fuller test for Google data.

    Parameters
    ----------
    goog : `pd.DataFrame`
    A DataFrame containing Google (GOOG) OHLCV data from
    01/09/2004-31/08/2020. Index is a Datetime object.

    Returns
    -------
    None
    """
    # Output the results of the Augmented Dickey-Fuller test for Google
    # with a lag order value of 1
    adf = ts.adfuller(goog['Adj Close'], 1)
    print(adf)


if __name__ == "__main__":
    data_csv = "PATH/TO/YOUR/GOOG.csv"
    goog_df = create_dataframe(data_csv)
    goog_adf = augmented_dickey_fuller(goog_df)
