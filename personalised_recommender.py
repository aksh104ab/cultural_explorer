# model/personalized_recommender.py
from sentence_transformers import SentenceTransformer, util
import pandas as pd

model = SentenceTransformer('all-MiniLM-L6-v2')

def recommend_by_interest(df, user_input, top_k=5):
    df = df.dropna(subset=['article_info']).copy()
    user_vec = model.encode(user_input)
    df['embedding'] = df['article_info'].apply(lambda x: model.encode(x))
    df['similarity'] = df['embedding'].apply(lambda x: util.cos_sim(user_vec, x).item())
    return df.sort_values('similarity', ascending=False).head(top_k)
