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
    A DataFrame containing OHLCV data. Index is a Datetime object.

    """
    # Create a pandas DataFrame containing the OHLCV data
    df = pd.read_csv(data_csv, index_col="Date")
    # Convert index to a Datetime object
    df.index = pd.to_datetime(df.index)
    return df


def augmented_dickey_fuller(df):
    """
    Carry out the Augmented Dickey-Fuller test for OHLCV data.

    Parameters
    ----------
    df : `pd.DataFrame`
    A DataFrame containing OHLCV data. Index is a Datetime object.

    Returns
    -------
    None
    """
    # Output the results of the Augmented Dickey-Fuller test for OHLCV data
    # with a lag order value of 1
    adf = ts.adfuller(df['Adj Close'], 1)
    print(adf)


if __name__ == "__main__":
    data_csv = "PATH/TO/YOUR/GOOG.csv"
    df = create_dataframe(data_csv)
    augmented_dickey_fuller(df) 
    