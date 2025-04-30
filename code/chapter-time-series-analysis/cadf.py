import matplotlib.pyplot as plt
import os
import pandas as pd
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts


def create_price_dataframe(path):
    """
    Read pricing data csv download for USO and XOM
    OHLCV data from 01/01/2019-01/01/2020 into DataFrames.

    Parameters
    ----------
    path : `str`
        Directory location of CSV files containing USO and XOM data.

    Returns
    -------
    price_df : `pd.DataFrame`
        A DataFrame containing XOM and USO Adjusted Close data from
        01/01/2019-01/01/2020. Index is a Datetime object.

    """
    uso = pd.read_csv(
        os.path.join(csv_path, "USO.csv"),
        index_col=0,
        parse_dates=True
    )
    xom = pd.read_csv(
        os.path.join(csv_path, "XOM.csv"),
        index_col=0,
        parse_dates=True
    )

    # Select columns to add to new DataFrame
    price_data = [uso["Adj Close"], xom["Adj Close"]]
    # Create headers for the columns
    headers = ["USO Price($)", "XOM Price($)"]
    # Concatenate xom and uso DataFrames using the index column
    price_df = pd.concat(price_data, axis=1, keys=headers)
    return price_df


def plot_price_series(price_df):
    """
    Plot the Adjusted Close price series for XOM and USO.

    Parameters
    ----------
    price_df : `pd.DataFrame`
        A DataFrame containing XOM and USO Adjusted Close data from
        01/01/2019-01/01/2020. Index is a Datetime object.

    Returns
    -------
    None
    """
    fig = price_df.plot(title="USO and XOM Daily Prices")
    fig.set_ylabel("Price($)")
    plt.show()


def plot_scatter_series(price_df):
    """
    Plot the Scatter plot of the XOM and USO price series.

    Parameters
    ----------
    price_df : `pd.DataFrame`
        A DataFrame containing XOM and USO Adjusted Close data from
        01/01/2019-01/01/2020. Index is a Datetime object.
    
    Returns
    -------
    None
    """
    price_df.plot.scatter(x=0, y=1, title="USO and XOM Price Scatterplot")
    plt.show()


def create_residuals(price_df):
    """
    Calculate the OLS and create the beta hedge ratio and residuals for the
    two equites XOM and USO.

    Parameters
    ----------
    price_df : `pd.DataFrame`
        A DataFrame containing XOM and USO Adjusted Close data from
        01/01/2019-01/01/2020. Index is a Datetime object.

    Returns
    -------
    price_df : `pd.DataFrame`
        Updated DataFrame with column values for beta hedge ratio (beta_hr)
        and residuals (Residuals).
    """
    # Create OLS model
    Y = price_df['USO Price($)']
    x = price_df['XOM Price($)']
    x = sm.add_constant(x)
    model = sm.OLS(Y, x)
    res = model.fit()
    
    # Beta hedge ratio (coefficent from OLS)
    beta_hr = res.params[1]
    print(f'Beta Hedge Ratio: {beta_hr}')
    
    # Residuals
    price_df["Residuals"] = res.resid
    return price_df


def create_cadf(price_df):
    """
    Calculate the Cointegrated Augmented Dickey Fuller test on the residuals.

    Parameters
    ----------
    price_df : `pd.DataFrame`
        Updated DataFrame with column values for beta hedge ratio (beta_hr)
        and residuals (Residuals).
    
    Returns
    -------
    cadf : `tuple`
        Results of ADF test on residuals including the test statistic,
        pvalue and critical values.
    """
    cadf = ts.adfuller(price_df["Residuals"])
    print(f'CADF:{cadf}')
    return cadf


def plot_residuals(price_df):
    """
    Plot the residuals.

    Parameters
    ----------
    price_df : `pd.DataFrame`
        Updated DataFrame with column values for beta hedge ratio (beta_hr)
        and residuals (Residuals).
    
    Returns
    -------
    None
    """
    price_df.plot(y="Residuals", title="Residual Plot", figsize=(8.6, 5.3))
    plt.ylabel("Price($)")
    plt.show()


if __name__ == "__main__":
    csv_path = "Path/To/Your/Directory/"

    price_dataframe = create_price_dataframe(csv_path)
    plot_price_series(price_dataframe)
    plot_scatter_series(price_dataframe)
    residuals_dataframe = create_residuals(price_dataframe)
    cadf_dataframe = create_cadf(residuals_dataframe)
    plot_residuals(residuals_dataframe)
