# plot_sharpe.py

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def create_dataframe(csv_file, lookback):
    df = pd.read_csv(csv_file, index_col=0)
    lookback_df = df.loc[df['ols_win'] == 100]
    lookback_df = lookback_df.reset_index(drop=True)
    return lookback_df


def create_sharpe_df(lookback_df):
    sharpe_df = lookback_df.pivot(
        columns='z_low', index='z_high', values='Sharpe'
    )
    return sharpe_df


def create_maxdd_df(lookback_df):
    maxdd_df = lookback_df.pivot(
        columns='z_low', index='z_high', values='Max Drawdown'
    )
    return maxdd_df


def create_heatmap(sharpe_df, maxdd_df):
    fig, axs = plt.subplots(1,2, figsize=(16, 10))
    
    sns.heatmap(sharpe_df, ax=axs[0], annot=True, cmap='YlGn')
    sns.heatmap(maxdd_df, ax=axs[1], annot=True, cmap='YlOrRd')
    axs[0].title.set_text("Sharpe Ratio")
    axs[1].title.set_text("Max Drawdown")
    plt.show()


if __name__ == "__main__":
    csv_file ="output.csv"
    lookback = 100
    df = create_dataframe(csv_file, lookback)
    sharpe_df = create_sharpe_df(df)
    maxdd_df = create_maxdd_df(df)
    create_heatmap(sharpe_df, maxdd_df)
