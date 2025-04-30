# forecast.py

from datetime import datetime as dt
import os

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import (
    LinearDiscriminantAnalysis as LDA, 
    QuadraticDiscriminantAnalysis as QDA
)
from sklearn.metrics import confusion_matrix
from sklearn.svm import LinearSVC, SVC


def create_dataframe(spy):
    """
    Read pricing data CSV download for SPY
    OHLCV data from 12/01/2015-31/12/2017 into a DataFrame.

    Parameters
   -----------
   spy : `csv`
       CSV file containing pricing data.
    
    Returns
    -------
    ts : `pd.DataFrame`
        A DataFrame containing SPY OHLCV data from
        12/01/2015-31/12/2017. Index is a DateTime object.
   
   """
    # obtain stock information
    ts = pd.read_csv(spy)
    ts = ts.set_index(pd.DatetimeIndex(ts['Date']))
    return ts


def create_lagged_df(ts, lags=5):
    """
    Create a n lagged time series where n is equal to 
    number of lags. Each time series contains the Adjusted Close price 
    and lags behind the original by n days.

    Parameters
    -----------
    ts : `pd.DataFrame`
        A DataFrame containing SPY OHLCV data from
        12/01/2015-31/12/2017. Index is a DateTime object.
    lags : `int`
        default = 5. The number of lags to create.
    Returns
    -------
    tslag : `pd.DataFrame`
        A DataFrame containg the original time series
        and five lagged time series where Adjusted Close
        price is shifted by the given lag.

    """
    # create lagged dataframe
    tslag = pd.DataFrame(index=ts.index)
    tslag["Today"] = ts["Adj Close"]
    tslag["Volume"] = ts["Volume"]

    # create the shifted lag series of prior trading period close values
    for i in range(0, lags):
        tslag[f"Lag{i+1}"] = ts["Adj Close"].shift(i+1)
    return tslag


def create_returns_df(tslag, lags=5):
    """
    Converts tslag from adjusted close price to a returns series using
    Pandas pct_change() function. 

    Parameters
    ----------
    tslag : `pd.Dataframe`
        a Dataframe containing the original time series
        and five lagged time series where adjusted close
        price is shifted by the given lag.
    lags : `int`
        default = 5. The number of lags to create.
    
    Returns
    -------
    tsret : `pd.Dataframe`
        a Dataframe containing the returns series for the original and 
        lagged time series.

    """
    # Create the returns dataframe
    tsret = pd.DataFrame(index=tslag.index)
    tsret["Volume"] = tslag['Volume']
    tsret["Today"] = tslag["Today"].pct_change()*100.0

    # If any of the values of percentage returns are zero, set them to
    # a small number. This stops issues with QDA model.
    tsret.loc[:, 'Today'] = tsret.apply(
        lambda row: 0.0001 if abs(row['Today']) < 0.0001 else row['Today'], 
        axis=1
    )

    # Create the lagged percentage returns columns
    for i in range(0, lags):
        tsret[f"Lag{i+1}"] = tslag[f"Lag{i+1}"].pct_change()*100.0 
    return tsret


def add_direction(tsret, start_date):
    """
    Adds a direction column to the DataFrame. Uses np.sign; gives negative 
    returns -1 and positive returns 1.

    Parameters
    ----------
    tsret : `pd.DataFrame`
        A DataFrame containing the returns series for the original and 
        lagged time series.
    start_date : `DateTime`
        The start date for the data. This removes NaNs created by
        the lag.
    Returns
    -------
    snpret : `pd.DataFrame`
        The final DataFrame with the lagged returns series and the direction.
    """
    # Create a "Direction" column (+1 or -1) indicating an up/down day
    tsret["Direction"] = np.sign(tsret["Today"])
    tsret = tsret[tsret.index >= start_date]
    return tsret


def create_test_train_sets(snpret):
    """
    Creates the train and test sets for the models. 

    Parameters
    ----------
    snpret : `pd.DataFrame`
        A DataFrame containing the returns series for the original and 
        lagged time series.
    
    Returns
    -------
    X_train : `pd.DataFrame`
        A Dataframe containing the training predictors to train the model.
    X_test : `pd.DataFrame`
        A DataFrame containing the training predictors to test the model.
    y_train : `pd.DataFrame`
        A DataFrame containing the training response set.
    pred : `pd.DataFrame`
        A DataFrame containing the predictions.
    """
    # Use the prior two days of returns as predictor values, 
    # with direction as the response
    X = snpret[["Lag1","Lag2"]]
    y = snpret["Direction"]

    # The test data is split into two parts: Before and after 1st Jan 2005.
    start_test = dt(2017,1,1)

    # Create training and test sets
    X_train = X[X.index < start_test]
    X_test = X[X.index >= start_test]
    y_train = y[y.index < start_test]
    y_test = y[y.index >= start_test]

    # Create prediction DataFrame
    pred = pd.DataFrame(index=y_test.index)
    pred["Actual"] = y_test
    return (X_train, X_test, y_train, y_test, pred)


if __name__ == "__main__":
    spy = "PATH/TO/YOUR/CSV"
    df = create_dataframe(spy)
    lagged_df = create_lagged_df(df, lags=5)
    lagged_returns = create_returns_df(lagged_df, lags=5)
    snpret = add_direction(lagged_returns, dt(2016, 1, 10))
    X_train, X_test, y_train, y_test, pred = create_test_train_sets(snpret)
   
    # Create the (parametrised) models
    print('Hit Rates/Confusion Matrices:\n')
    models = [
        ('LR', LogisticRegression(solver='liblinear')), 
        ('LDA', LDA(solver='svd')), 
        ('QDA', QDA()),
        ('LSVC', LinearSVC(max_iter=10000)),
        ('RSVM', SVC(
            C=1000000.0, cache_size=200, class_weight=None,
            coef0=0.0, degree=3, gamma=0.0001, kernel='rbf',
            max_iter=-1, probability=False, random_state=None,
            shrinking=True, tol=0.001, verbose=False)
        ),
        ('RF', RandomForestClassifier(
            n_estimators=1000, criterion='gini', 
            max_depth=None, min_samples_split=2, 
            min_samples_leaf=1, max_features='sqrt', 
            bootstrap=True, oob_score=False, n_jobs=1, 
            random_state=None, verbose=0)
        )
    ]
    # Iterate through the models
    for m in models:
        # Train each of the models on the training set
        m[1].fit(X_train, y_train)

        # Make an array of predictions on the test set
        pred = m[1].predict(X_test)

        # Output the hit-rate and the confusion matrix for each model
        print('%s:\n%0.3f' % (m[0], m[1].score(X_test, y_test)))
        print('%s\n' % confusion_matrix(pred, y_test))
