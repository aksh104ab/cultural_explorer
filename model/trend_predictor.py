import pandas as pd
from sklearn.linear_model import LinearRegression

def train_trend_model(df):
    df['year'] = df['year'].astype(int)
    df['domestic_arrivals'] = df['domestic_arrivals'].astype(int)
    model = LinearRegression()
    X = df[['year']]
    y = df['domestic_arrivals']
    model.fit(X, y)
    return model

def predict_future(df, state, future_year):
    state_df = df[df['state'] == state]
    model = train_trend_model(state_df)
    pred = model.predict([[future_year]])
    return pred[0]
