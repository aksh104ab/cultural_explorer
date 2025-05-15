"""
trend_predictor.py

Synopsis:
----------
This module provides functions to train a linear regression model on tourism data and predict future domestic arrivals for a given state and year. 
It is used to analyze and forecast tourism trends based on historical data.

Functions:
    - train_trend_model(df): Trains a linear regression model using 'YEAR' and 'DOMESTIC_ARRIVALS'.
    - predict_future(df, state, future_year): Predicts domestic arrivals for a specific state and year using the trained model.
"""

import pandas as pd
from sklearn.linear_model import LinearRegression

def train_trend_model(df):
    df['YEAR'] = df['YEAR'].astype(int)
    df['DOMESTIC_ARRIVALS'] = df['DOMESTIC_ARRIVALS'].astype(int)
    model = LinearRegression()
    X = df[['YEAR']]
    y = df['DOMESTIC_ARRIVALS']
    model.fit(X, y)
    return model

def predict_future(df, state, future_year):
    state_df = df[df['STATE'] == state]
    model = train_trend_model(state_df)
    pred = model.predict([[future_year]])
    return pred[0]
