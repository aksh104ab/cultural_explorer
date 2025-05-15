"""
get_popular_site.py

Synopsis:
----------
This module provides functions to recommend top-rated cultural sites based on responsible tourism scores.
It allows filtering by overall score or by state to highlight the most responsible and highly rated destinations.

Functions:
    - recommend_sites(df, score_threshold=8.0): Returns sites with responsible score above the threshold.
    - recommend_sites_by_state(df, state, score_threshold=8.0): Returns top sites for a given state above the threshold.
"""

import pandas as pd

def recommend_sites(df, score_threshold=8.0):
    return df[df['RESPONSIBLE_SCORE'] >= score_threshold].sort_values(by='RESPONSIBLE_SCORE', ascending=False)

def recommend_sites_by_state(df, state, score_threshold=8.0):
    # Filter by state and responsible score
    return df[(df['STATE'] == state) & (df['RESPONSIBLE_SCORE'] >= score_threshold)].sort_values(by='RESPONSIBLE_SCORE', ascending=False)
