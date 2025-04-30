# create_lagged_series.py

import os

import numpy as np
import pandas as pd

def create_lagged_series(symbol, start_date, end_date, lags=5):

    spy = "PATH/TO/YOUR/CSV"
    
    # obtain stock information
    ts = pd.read_csv(spy)
    ts = ts.set_index(pd.DatetimeIndex(ts['timestamp']))
    
    # create lagged dataframe
    tslag = pd.DataFrame(index=ts.index)
    tslag["today"] = ts["adjusted_close"]
    tslag["volume"] = ts["volume"]
    for i in range(0, lags):
        tslag[f"Lag{i+1}"] = ts["adjusted_close"].shift(i+1)

    # create the returns dataframe
    tsret = pd.DataFrame(index=tslag.index)
    tsret["volume"] = tslag['volume']
    tsret["today"] = tslag["today"].pct_change()*100.0

    # if any of the values of percentage returns are zero, set them to
    # a small number. this stops issues with qda model.
    tsret.loc[:, 'today'] = tsret.apply(
        lambda row: 0.0001 if abs(row['today']) < 0.0001 else row['today'], 
        axis=1
    )

    # create the lagged percentage returns columns
    for i in range(0, lags):
        tsret[f"Lag{i+1}"] = tslag[f"Lag{i+1}"].pct_change()*100.0 
    # Create the "Direction" column (+1 or -1) indicating an up/down day
    tsret["Direction"] = np.sign(tsret["today"])
    tsret = tsret[tsret.index >= start_date]

    return tsret
