import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.trend_predictor import predict_future
from model.site_recommender import recommend_sites

# Load data
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')

csv_sites = os.path.join(DATA_DIR, 'cultural_sites.csv')
csv_trends = os.path.join(DATA_DIR, 'tourism_stats.csv')

df_sites = pd.read_csv(csv_sites)
df_trends = pd.read_csv(csv_trends)

st.set_page_config(page_title="India's Cultural Tourism AI Explorer", page_icon="🎨", layout="wide")
st.title("🇮🇳 India's Cultural Tourism AI Explorer")

# Tabs
tab1, tab2, tab3 = st.tabs(["🗺 Explore Sites", "📈 Predict Trends", "🤖 Smart Recommendations"])

with tab1:
    st.subheader("Explore Hidden Cultural Gems")
    # Center on India and zoom in
    m = folium.Map(
        location=[22.5937, 78.9629],  # Center of India
        zoom_start=5.5,               # Zoom so India fills the map
        min_lat=6, max_lat=38,        # Optional: restrict panning
        min_lon=68, max_lon=98
    )
    m.fit_bounds([[6, 68], [38, 98]])  # SouthWest and NorthEast corners of India
    for _, row in df_sites.iterrows():
        # Infographics popup with image and details
        popup_html = f"""
        <div style='width:220px'>
            <h4 style='margin-bottom:4px'>{row['site_name']}</h4>
            <img src="{row['image_url']}" width="200" style='border-radius:8px; margin-bottom:6px'><br>
            <b>State:</b> {row['state']}<br>
            <b>Art Form:</b> {row['art_form']}<br>
            <b>Seasonality:</b> {row['seasonality']}<br>
            <b>Responsible Score:</b> {row['responsible_score']}
        </div>
        """
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=row['state']
        ).add_to(m)
    folium_static(m)
    
    st.subheader("Filter by Art Form")
    selected_art = st.selectbox("Select Art Form", df_sites['art_form'].unique())
    st.dataframe(df_sites[df_sites['art_form'] == selected_art])

with tab2:
    st.subheader("State-wise Tourism Trend Prediction")
    state = st.selectbox("Select State", df_trends['state'].unique())
    year = st.slider("Select Future Year", 2021, 2030, 2025)
    pred = predict_future(df_trends, state, year)
    st.info(f"Predicted domestic arrivals in {state} for {year}: {int(pred):,}")

    fig = px.line(df_trends[df_trends['state'] == state], x='year', y='domestic_arrivals', title=f"{state} Tourism Trends")
    st.plotly_chart(fig)

with tab3:
    st.subheader("AI-driven Responsible Site Recommendations")
    recommended = recommend_sites(df_sites)
    st.dataframe(recommended)

st.markdown("---")
st.info("Data & AI by Snowflake, ML, and Streamlit | Promoting Responsible Tourism")

