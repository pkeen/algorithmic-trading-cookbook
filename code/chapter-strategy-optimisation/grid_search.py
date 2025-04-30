# grid_search.py
import pprint
from datetime import datetime as dt

from sklearn.model_selection import train_test_split, GridSearchCV, TimeSeriesSplit 
from sklearn.metrics import classification_report
from sklearn.svm import SVC

from create_lagged_series import create_lagged_series


if __name__ == "__main__":
    # Create a lagged series of the S&P500 US stock market index
    snpret = create_lagged_series(
        "SPY", dt(2016,1,10), 
        dt(2017,12,31), lags=5
    )

    # Use the prior two days of returns as predictor 
    # values, with direction as the response
    X = snpret[["Lag1","Lag2"]]
    y = snpret["Direction"]

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.5, shuffle=False 
    )

    # Set the parameters by cross-validation
    tuned_parameters = [
        {'kernel': ['rbf'], 'gamma': [1, 1e-1, 1e-2, 1e-3], 'C': [0.1, 1, 10, 100]}
    ]

    # Perform the grid search on the tuned parameters
    model = GridSearchCV(SVC(C=1), tuned_parameters, cv=TimeSeriesSplit(n_splits=3))
    model.fit(X_train, y_train)

    print("Optimised parameters found on training set:")
    print(model.best_estimator_, "\n")
    
    print("Mean scores calculated:")
    scores = model.cv_results_['mean_test_score']
    params = model.cv_results_['params']
    for idx, score in enumerate(scores):
        print(f"{score:.3f} for {params[idx]}")
