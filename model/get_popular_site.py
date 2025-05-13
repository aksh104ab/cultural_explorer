import pandas as pd

def recommend_sites(df, score_threshold=8.0):
    return df[df['responsible_score'] >= score_threshold].sort_values(by='responsible_score', ascending=False)
