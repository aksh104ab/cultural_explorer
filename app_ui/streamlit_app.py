import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import sys
import os
import random
import snowflake.connector
#from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.trend_predictor import predict_future
from model.get_popular_site import recommend_sites, recommend_sites_by_state
from model.personalised_recommender import recommend_by_interest

# Load environment variables
#load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'pass.env'))

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        # Load Font Awesome for social icons
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
""", unsafe_allow_html=True)

local_css(os.path.join(os.path.dirname(__file__), 'styles', 'styles.css'))

# --------- Snowflake Connection & Data Fetch ---------
@st.cache_data(show_spinner="Loading data from Snowflake...")
def fetch_data_from_snowflake():
    conn = snowflake.connector.connect(
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PASSWORD'],
        account=os.environ['SNOWFLAKE_ACCOUNT'],
        warehouse=os.environ['SNOWFLAKE_WAREHOUSE'],
        database=os.environ['SNOWFLAKE_DATABASE'],
        schema=os.environ['SNOWFLAKE_SCHEMA']
    )
    # Fetch cultural sites
    df_sites = pd.read_sql(
        "SELECT site_name, state, art_form, seasonality, responsible_score, latitude, longitude, image_url, describtion FROM cultural_sites",
        conn
    )
    # Fetch tourism stats
    df_trends = pd.read_sql(
        "SELECT state, year, domestic_arrivals FROM tourism_stats",
        conn
    )
    conn.close()
    return df_sites, df_trends

df_sites, df_trends = fetch_data_from_snowflake()

# App Header
st.markdown("""
    <div class='header-box'>
        <h1>BharatVerse - Cultural Tourism Explorer</h1>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "**🗺 Explore Sites**", 
    "**📈 Predict Trends**", 
    "**🗺️ Recommented Top Rated Sites**", 
    "**🧠 AI based Sites Recommendations**"
])

# -------- Tab 1: Map + Featured Site --------
with tab1:
    st.subheader("Explore Hidden Cultural Gems -")
    st.markdown("""
    Use the map to explore unique festivals, art forms, and heritage sites across the country.  
    Filter by art form to see how diverse traditions flourish in different regions.
    """)
    col1, col2 = st.columns([1.6, 1], gap="small")

    with col1:
        selected_art = st.selectbox("Select Art Form", df_sites['ART_FORM'].unique(), key="art_form_selector")
        filtered_df = df_sites[df_sites['ART_FORM'] == selected_art]

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
                    <h4 style='margin-bottom:4px'>{row['SITE_NAME']}</h4>
                    <img src="{row['IMAGE_URL']}" width="200" style='border-radius:8px; margin-bottom:6px'><br>
                    <b>State:</b> {row['STATE']}<br>
                    <b>Art Form:</b> {row['ART_FORM']}<br>
                    <b>Seasonality:</b> {row['SEASONALITY']}<br>
                    <b>Responsible Score:</b> {row['RESPONSIBLE_SCORE']}<br>
                </div>
                """
                folium.Marker(
                    location=[row['LATITUDE'], row['LONGITUDE']],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=row['STATE']
                ).add_to(m)
            st.session_state[map_key] = m

        st.markdown("<div class='map-container'>", unsafe_allow_html=True)
        folium_static(st.session_state[map_key], height=350 + 40 * len(filtered_df))
        st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("###### Featured Cultural Site")
            if "featured_site_idx" not in st.session_state:
                st.session_state["featured_site_idx"] = random.randint(0, len(df_sites) - 1)

            if st.button("🔄 Show Another Site", key="change_featured_site"):
                st.session_state["featured_site_idx"] = random.randint(0, len(df_sites) - 1)

            featured = df_sites.iloc[st.session_state["featured_site_idx"]]
            st.markdown(f"""
                <div class="site-card">
                    <h4 style="color:#a63603;">{featured['SITE_NAME']}</h4>
                    <img src="{featured['IMAGE_URL']}" width="100%" style="border-radius:8px; margin-bottom:6px">
                    <p><b>State:</b> {featured['STATE']}<br>
                       <b>Art Form:</b> {featured['ART_FORM']}<br>
                       <b>Best Time:</b> {featured['SEASONALITY']}</p>
                    <p style="font-size:0.9rem">{featured['DESCRIBTION']}</p>
                </div>
            """, unsafe_allow_html=True)
        
            facts_df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'data', 'cultural_facts.csv'))
            facts = facts_df['fact'].tolist()

            if st.button("🔁 Show Cultural Fact"):
                st.info(random.choice(facts))

# -------- Tab 2: Tourism Trends --------
with tab2:
    st.subheader("📈 State-wise Tourism Trend Prediction")
    st.markdown("""
    Analyze tourism trends for each state using real data.  
    Select a state and a future year to see predicted visitor numbers, and visualize how cultural tourism is evolving over time.
    """)
    state = st.selectbox("Select State", df_trends['STATE'].unique())
    year = st.slider("Select Future Year", 2021, 2030, 2025)
    pred = predict_future(df_trends, state, year)
    st.markdown(
        f"📊 Predicted domestic arrivals in <b>{state}</b> for <b>{year} : {int(pred):,}</b>",
        unsafe_allow_html=True
    )
    fig = px.line(df_trends[df_trends['STATE'] == state], x='YEAR', y='DOMESTIC_ARRIVALS', title=f"{state} Tourism Trends")
    st.plotly_chart(fig)
    st.markdown("""
    *Use these insights to plan your trips during less crowded seasons and discover emerging destinations!
    """)

# -------- Tab 3: Top Rated Sites -Recommendation --------
with tab3:
    st.subheader(" Top Rated Cultural Sites by State")
    st.markdown("""
    Discover the highest-rated cultural sites for responsible tourism in each state.  
    Select a state to see which destinations stand out for their cultural value, sustainability, and visitor experience.
    """)
    state_selected = st.selectbox("Select State for Top Sites", df_sites['STATE'].unique(), key="recommend_state")
    recommended = recommend_sites_by_state(df_sites, state_selected)
    st.dataframe(recommended[['SITE_NAME', 'STATE', 'ART_FORM', 'DESCRIBTION']], hide_index=True)
    st.markdown("""
    These sites are recognized for their commitment to preserving heritage and promoting sustainable travel.
    """)

# -------- Tab 4: AI/NLP Recommender --------
with tab4:
    st.subheader("🧠 AI ML Based Cultural sites Recommender ")
    st.markdown("""
    Get personalized recommendations!  
    Describe your interests (e.g., "I like spiritual places and classical dance") and let our AI suggest the best cultural sites for you.
    """)
    user_input = st.text_area("Describe your interests (e.g., 'I like spiritual places and classical dance'):")

    if user_input:
        st.markdown("🔍 **Top Cultural Sites Matching Your Interests:**")
        top_matches = recommend_by_interest(df_sites, user_input)
        st.dataframe(top_matches[['SITE_NAME', 'STATE', 'DESCRIBTION']], hide_index=True)
        st.markdown("""
        Our AI matches your interests with above sites, helping you discover hidden gems tailored to your preferences!_
        """)

# -------- Footer --------
st.markdown("""
<div class="footer-bar">
    <div class="footer-content">
        © 2025 BharatVerse Cultural Tourism Explorer.
    </div>
    <div class="footer-icons">
        <a href="https://twitter.com/yourprofile" target="_blank"><i class="fab fa-twitter"></i></a>
        <a href="https://linkedin.com/in/yourprofile" target="_blank"><i class="fab fa-linkedin"></i></a>
        <a href="https://github.com/yourrepo" target="_blank"><i class="fab fa-github"></i></a>
    </div>
</div>
""", unsafe_allow_html=True)

