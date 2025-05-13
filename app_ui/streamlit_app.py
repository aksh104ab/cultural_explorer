import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.trend_predictor import predict_future
from model.get_popular_site import recommend_sites
from model.personalised_recommender import recommend_by_interest

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css(os.path.join(os.path.dirname(__file__), 'styles', 'styles.css'))

# Load Data
csv_sites = "F:/cultural_explorer/data/cultural_sites.csv"
csv_trends = "F:/cultural_explorer/data/tourism_stats.csv"

df_sites = pd.read_csv(csv_sites)
df_trends = pd.read_csv(csv_trends)

# App Header
st.markdown("""
    <div class='header-box'>
        <h1>🇮🇳 India's Cultural Tourism AI Explorer</h1>
        <p>Discover art, heritage, and hidden gems across India — powered by AI.</p>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺 Explore Sites", 
    "📈 Predict Trends", 
    "🤖 Smart Recommendations", 
    "🧠 Personalized Explorer"
])

# -------- Tab 1: Map + Featured Site --------
with tab1:
    st.subheader("Explore Hidden Cultural Gems")

    col1, col2 = st.columns([1.6, 1], gap="small")

    with col1:
        # 🎨 Filter below map — this won't cause map to refresh
        #st.subheader("🎨 Filter by Art Form")
        selected_art = st.selectbox("Select Art Form", df_sites['art_form'].unique(), key="art_form_selector")
        filtered_df = df_sites[df_sites['art_form'] == selected_art]

        # Cache the map once per art form filter
        map_key = f"folium_map_{selected_art}"
        if map_key not in st.session_state:
            m = folium.Map(
                location=[22.5937, 78.9629],
                zoom_start=5.5,
                min_lat=6, max_lat=38,
                min_lon=68, max_lon=98
            )
            m.fit_bounds([[6, 68], [38, 98]])
            for _, row in filtered_df.iterrows():
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
            st.session_state[map_key] = m

        st.markdown("<div class='map-container'>", unsafe_allow_html=True)
        folium_static(st.session_state[map_key], height=350 + 40 * len(filtered_df))
        st.markdown("</div>", unsafe_allow_html=True)

        st.dataframe(filtered_df)



    with col2:
        featured = df_sites.sample(1).iloc[0]
        st.markdown(f"""
            <div class="site-card">
                <h4 style="color:#a63603;">🌟 Featured: {featured['site_name']}</h4>
                <img src="{featured['image_url']}" width="100%" style="border-radius:8px; margin-bottom:6px">
                <p><b>State:</b> {featured['state']}<br>
                   <b>Art Form:</b> {featured['art_form']}<br>
                   <b>Best Time:</b> {featured['seasonality']}</p>
                <p style="font-size:0.9rem">{featured['description']}</p>
            </div>
        """, unsafe_allow_html=True)

        facts = [
            "🎭 Kathakali makeup takes over 3 hours to apply.",
            "🕍 The Ajanta caves date back to 2nd century BCE!",
            "🗡️ Chhau dance uses masks and swords in its act.",
            "🌊 Kumbh Mela is the world's largest peaceful gathering.",
            "🎨 Madhubani art uses twigs and natural colors."
        ]
        if st.button("🔁 Show Cultural Fact"):
            st.info(random.choice(facts))

# -------- Tab 2: Tourism Trends --------
with tab2:
    st.subheader("📈 State-wise Tourism Trend Prediction")
    state = st.selectbox("Select State", df_trends['state'].unique())
    year = st.slider("Select Future Year", 2021, 2030, 2025)
    pred = predict_future(df_trends, state, year)
    st.info(f"📊 Predicted domestic arrivals in {state} for {year}: {int(pred):,}")
    fig = px.line(df_trends[df_trends['state'] == state], x='year', y='domestic_arrivals', title=f"{state} Tourism Trends")
    st.plotly_chart(fig)

# -------- Tab 3: Responsible Recommendations --------
with tab3:
    st.subheader("🤖 AI-driven Responsible Site Recommendations")
    recommended = recommend_sites(df_sites)
    st.dataframe(recommended)

# -------- Tab 4: AI/NLP Recommender --------
with tab4:
    st.subheader("🧠 AI-powered Cultural Recommender")
    user_input = st.text_area("Describe your interests (e.g., 'I like spiritual places and classical dance'):")

    if user_input:
        st.markdown("🔍 **Top Cultural Sites Matching Your Interests:**")
        top_matches = recommend_by_interest(df_sites, user_input)
        st.dataframe(top_matches[['site_name', 'state', 'art_form', 'description']])

# -------- Footer --------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <footer>
        Made with ❤️ using Streamlit, Snowflake, and OpenAI<br>
        © 2025 Cultural Explorer Hackathon Submission
    </footer>
""", unsafe_allow_html=True)
