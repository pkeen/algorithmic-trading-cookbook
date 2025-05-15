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
    df = pd.read_csv(data_csv, index_col="date")
    # Convert index to a Datetime object
    df.index = pd.to_datetime(df.index)
    return df

def print_adf_results(adf_result):
    adf_statistic, p_value, used_lag, n_obs, crit_values, ic_best = adf_result
    print("Augmented Dickey-Fuller Test Results")
    print(f"ADF Statistic:      {adf_statistic:.4f}")
    print(f"p-value:            {p_value:.4f}")
    print(f"# Lags Used:        {used_lag}")
    print(f"# Observations Used:{n_obs}")
    print("Critical Values:")
    for key, value in crit_values.items():
        print(f"   {key}: {value:.4f}")
    print(f"IC Best:            {ic_best:.4f}")



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
    adf = ts.adfuller(df['adjClose'], 1)
    print_adf_results(adf)


if __name__ == "__main__":
    data_csv = "./data/AAPL_2023-01-01_to_2025-05-15.csv"
    df = create_dataframe(data_csv)
    augmented_dickey_fuller(df) 
    