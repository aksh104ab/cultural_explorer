"""
personalised_recommender.py

Synopsis:
----------
This module provides a function to recommend cultural sites based on user interests using NLP.
It leverages sentence-transformers to compute semantic similarity between user input and site descriptions,
returning the most relevant sites as personalized recommendations.

Functions:
    - recommend_by_interest(df, user_input, top_k=1): Returns top-k sites matching user interests.
"""

from sentence_transformers import SentenceTransformer, util
import pandas as pd

model = SentenceTransformer('all-MiniLM-L6-v2')

def recommend_by_interest(df, user_input, top_k=2):
    df = df.dropna(subset=['DESCRIBTION']).copy()
    user_vec = model.encode(user_input)
    df['embedding'] = df['DESCRIBTION'].apply(lambda x: model.encode(x))
    df['similarity'] = df['embedding'].apply(lambda x: util.cos_sim(user_vec, x).item())
    return df.sort_values('similarity', ascending=False).head(top_k)
