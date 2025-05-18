import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import random
import snowflake.connector
#from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.trend_predictor import predict_future
from model.get_popular_site import recommend_sites, recommend_sites_by_state
from model.personalised_recommender import recommend_by_interest
import numpy as np

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
    <div style="background: linear-gradient(90deg, #ffe066 0%, #b7e4c7 60%, #a7c7e7 100%); box-shadow: 0 4px 18px #e0e0e0; padding: 18px 12px 14px 12px; margin-bottom: 18px; display: flex; align-items: center; gap: 18px;">
        <img src="https://img.icons8.com/color/96/india.png" alt="India Icon" style="width:54px; height:54px; box-shadow:0 2px 8px #b7e4c7">
        <span style="font-family:'Segoe UI',Arial,sans-serif;">
            <span style="font-size:2.2em; color:#218838; font-weight:900; letter-spacing:1.5px; text-shadow:0 2px 8px #ffe066, 0 4px 16px #a7c7e7;">Bharat<span style="color:#a63603;">Verse</span></span>
            <span style="font-size:1.25em; color:#007f5f; font-weight:500; margin-left:12px; letter-spacing:0.7px; text-shadow:0 1px 6px #ffe066;">Cultural Tourism Explorer</span>
        </span>
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
    st.subheader("Explore India's Hidden Cultural Jewels")
    st.markdown("""
    <div>
        <b>Embark on a journey through India's vibrant heritage!</b><br>
        <span style="color:#a63603;">Zoom in</span> to discover dazzling festivals, <span style="color:#388e3c;">iconic art forms</span>, and <span style="color:#007f5f;">timeless wonders</span>.
        <span style="color:#555;">Filter by art form and watch traditions bloom across the map.</span>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([1.7, 1], gap="medium")

    with col1:
        selected_art = st.selectbox(
            "Select an Art Form to Reveal Its Magic -",
            df_sites['ART_FORM'].unique(),
            key="art_form_selector"
        )
        filtered_df = df_sites[df_sites['ART_FORM'] == selected_art]

        map_key = f"folium_map_{selected_art}"
        if st.session_state.get("last_map_art_form") != selected_art or map_key not in st.session_state:
            m = folium.Map(
                location=[22.5937, 78.9629],
                zoom_start=5.5,
                min_lat=6, max_lat=38,
                min_lon=68, max_lon=98
            )
            m.fit_bounds([[6, 68], [38, 98]])
            for _, row in filtered_df.iterrows():
                popup_html = f"""
                <div style='width:230px; font-family:Segoe UI,Arial,sans-serif;'>
                    <h4 style='margin-bottom:4px; color:#218838; font-size:1.13em;'>{row['SITE_NAME']}</h4>
                    <img src="{row['IMAGE_URL']}" width="210" style='border-radius:10px; margin-bottom:7px; border:2px solid #b7e4c7'><br>
                    <b>State:</b> <span style="color:#a63603;">{row['STATE']}</span><br>
                    <b>Art Form:</b> <span style="color:#388e3c;">{row['ART_FORM']}</span><br>
                    <b>Seasonality:</b> <span style="color:#007f5f;">{row['SEASONALITY']}</span><br>
                    <b>Responsible Score:</b> <span style="color:#218838;">{row['RESPONSIBLE_SCORE']}</span>
                </div>
                """
                folium.Marker(
                    location=[row['LATITUDE'], row['LONGITUDE']],
                    popup=folium.Popup(popup_html, max_width=260),
                    tooltip=f"{row['SITE_NAME']} ({row['STATE']})"
                ).add_to(m)
            st.session_state[map_key] = m
            st.session_state["last_map_art_form"] = selected_art

        st.markdown("<div class='map-container'>", unsafe_allow_html=True)
        folium_static(st.session_state[map_key], height=370 + 35 * len(filtered_df))
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        if "featured_site_idx" not in st.session_state:
            st.session_state["featured_site_idx"] = random.randint(0, len(df_sites) - 1)

        if st.button("▶ Click to see next Hidden Gem", key="change_featured_site"):
            st.session_state["featured_site_idx"] = random.randint(0, len(df_sites) - 1)

        featured = df_sites.iloc[st.session_state["featured_site_idx"]]
        st.markdown(f"""
            <div class="site-card" style="background:linear-gradient(90deg,#f6fff6 60%,#fffde7 100%); border-radius:16px; box-shadow:0 2px 12px #e0e0e0; padding:16px 14px; margin-bottom:14px;">
                <h4 style="color:#a63603; margin-bottom:8px; font-size:1.18em;">{featured['SITE_NAME']}</h4>
                <img src="{featured['IMAGE_URL']}" width="100%" style="border-radius:10px; margin-bottom:10px; border:2px solid #b7e4c7">
                <div style="font-size:1.04em; color:#388e3c; margin-bottom:7px;">
                    <b>State:</b> {featured['STATE']}<br>
                    <b>Art Form:</b> {featured['ART_FORM']}<br>
                    <b>Best Time:</b> {featured['SEASONALITY']}
                </div>
                <div style="font-size:1em; color:#444; margin-bottom:5px;">{featured['DESCRIBTION']}</div>
            </div>
        """, unsafe_allow_html=True)

        facts_df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'data', 'cultural_facts.csv'))
        facts = facts_df['fact'].tolist()

        if st.button("💡Surprise Me With a Cultural Fact"):
            st.info(f"{random.choice(facts)}")

# -------- Tab 2: Tourism Trends --------
with tab2:
    st.subheader("Indian Tourism: Past, Present & The Future!")
    st.markdown("""
    <div >
        <span style="font-size:1.18em; color:#218838;"><b>Where will the next wave of explorers go ?</b></span><br>
        <span style="color:#a63603;"><b>Visualize</b></span> the journey of Indian tourism, <span style="color:#388e3c;"><b>predict</b></span> the future, and <span style="color:#007f5f;"><b>plan your adventure</b></span> before the crowds arrive!<br>
        <span style="color:#555;">Select a state and a future year to see <b>projected visitor numbers</b> and animated trends. <br>
    </div>
    """, unsafe_allow_html=True)
    state = st.selectbox("🌏 Choose a State to Explore", df_trends['STATE'].unique())
    year = st.slider("📅 Pick a Future Year", 2025, 2030, 2025)
    pred = predict_future(df_trends, state, year)
    st.markdown(
        f"""
        <div style="background:linear-gradient(90deg,#b7e4c7 60%,#ffe066 100%); border-radius:12px; padding:18px 26px; margin-bottom:18px; display:inline-block; box-shadow:0 2px 10px #e0e0e0;">
            <span style="font-size:1.18em; color:#a63603;"><b>Prediction for {state}:</b></span><br>
            <span style="font-size:1.13em;">
                <b>{state}</b> is expected to welcome 
                <span style="background:#218838; border-radius:7px; padding:5px 14px; color:#fff; font-weight:700; font-size:1.18em;">{int(pred):,}</span>
                domestic tourists in <b>{year}</b>!
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Prepare data for animation
    state_data = df_trends[df_trends['STATE'] == state].sort_values('YEAR')
    years = state_data['YEAR'].tolist()
    arrivals = state_data['DOMESTIC_ARRIVALS'].tolist()
    arrivals_k = [round(a / 1000, 1) for a in arrivals]

    # Custom green gradient for bars
    green_shades = [
        "#e0ffe6", "#b7e4c7", "#95d5b2", "#74c69d", "#52b788", "#40916c", "#218838"
    ]
    color_seq = green_shades * ((len(years) // len(green_shades)) + 1)
    color_seq = color_seq[:len(years)]

    fig = px.bar(
        x=[str(y) for y in years],
        y=arrivals_k,
        labels={'x': 'Year', 'y': 'Domestic Arrivals (K)'},
        color=[str(y) for y in years],
        color_discrete_sequence=color_seq,
        title=f"📊 {state} Tourism Trends",
        text=[f"{a}K" for a in arrivals_k]
    )

    fig.update_traces(
        texttemplate='<b>%{text}</b>',
        textposition='outside',
        marker_line_color='#218838',
        marker_line_width=2.5,
        opacity=0.96,
        hovertemplate='<b>Year:</b> %{x}<br><b>Arrivals:</b> %{y}K<extra></extra>'
    )
    fig.update_layout(
        showlegend=False,
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Domestic Arrivals (in Thousands)</b>",
        plot_bgcolor="#f6fff6",
        paper_bgcolor="#f6fff6",
        title_font_size=28,
        title_font_color="#218838",
        font=dict(family="Segoe UI, Arial", size=18, color="#222"),
        bargap=0.15,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(size=17, color="#218838"),
            tickangle=-25,
            linecolor="#b7e4c7",
            linewidth=2.5
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#e0e0e0",
            zeroline=False,
            tickfont=dict(size=17, color="#388e3c"),
            linecolor="#b7e4c7",
            linewidth=2.5
        ),
        margin=dict(l=40, r=40, t=80, b=50),
        height=440,
        transition={'duration': 600, 'easing': 'cubic-in-out'}
    )
    fig.update_yaxes(tickformat=",")

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown("""
    <div>
        <b>Travel Hack:</b> Use these insights to <span style="color:#218838;">beat the crowds</span> and discover <span style="color:#a63603;">emerging hotspots</span> before they go viral!<br>
        <span style="color:#388e3c;">Plan your next adventure with confidence and curiosity.</span>
    </div>
    """, unsafe_allow_html=True)

# -------- Tab 3: Top Rated Sites -Recommendation --------
with tab3:
    st.subheader("India's Most Enchanting Cultural Wonders Await You!")
    st.markdown("""
    <div>
        <b>Step into a world of wonder!</b> <br>
        Discover the <span style="color:#218838;"><b>top-rated</b></span> cultural marvels in every state—handpicked for their <span style="color:#388e3c;"><b>authentic charm</b></span>, <span style="color:#007f5f;"><b>vivid traditions</b></span>, and <span style="#007f5f;"><b>unforgettable stories</b></span>.<br>
        <span style="color:#555;">Choose a state and unlock a curated list of must-see gems, perfect for the curious and the adventurous.</span>
    </div>
    """, unsafe_allow_html=True)
    state_selected = st.selectbox("Which State's Treasures Will You Explore ?", df_sites['STATE'].unique(), key="recommend_state")
    recommended = recommend_sites_by_state(df_sites, state_selected)

    st.markdown("<div style='display:flex; flex-direction:column; gap:28px;'>", unsafe_allow_html=True)
    for idx, row in recommended.iterrows():
        query = f"{row['SITE_NAME']} {row['STATE']}".replace(' ', '+')
        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={query}"
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; background:linear-gradient(90deg,#f6fff6 60%,#fffde7 100%); border-radius:15px; padding:15px 20px; margin-bottom:10px; min-height:110px; box-shadow:0 2px 8px #e0e0e0;">
                <img src="{row['IMAGE_URL']}" style="width:140px; height:100px; object-fit:cover; border-radius:10px; margin-right:22px; border:2px solid #b7e4c7;">
                <div style="flex:1;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span style="font-size:1.09em; color:#218838; font-weight:700;">{row['SITE_NAME']}</span>
                        <span style="font-size:1em; color:#388e3c;">({row['STATE']})</span>
                        <span style="background:#eaffd0; color:#218838; border-radius:5px; padding:2px 8px; font-size:0.93em; margin-left:8px;">
                            <i class="fa fa-star" style="color:#ffd700;"></i> Top Pick
                        </span>
                    </div>
                    <div style="font-size:0.98em; color:#333; margin:7px 0 0 0;">{row['DESCRIBTION']}</div>
                    <div style="margin-top:10px;">
                        <a href="https://www.google.com/search?q={query}" target="_blank" style="text-decoration:none;">
                            <button style="background:linear-gradient(90deg,#b7e4c7 60%,#fffde7 100%); color:#218838; border:none; border-radius:7px; padding:5px 13px; font-size:0.97em; display:flex; align-items:center; gap:7px; cursor:pointer; box-shadow:0 1px 4px #e0e0e0;">
                                <i class="fab fa-google" style="color:#218838; font-size:1.08em;"></i>
                                <span style="font-size:1em;">Explore More..</span>
                            </button>
                        </a>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

# -------- Tab 4: AI/NLP Recommender --------
with tab4:
    st.subheader("AI-Powered Cultural Site Recommender ")
    st.markdown("""
    Looking for your next unforgettable cultural adventure?  
    <b>Describe your passions, dreams, or what excites you about Indian culture</b> – and let our smart recommender unveil hidden gems just for you!
    """, unsafe_allow_html=True)
    user_input = st.text_area(
        "Tell us what inspires you (e.g., 'I'm fascinated by ancient temples and folk music', 'Love vibrant festivals and art villages'):"
    )

    if user_input:
        st.markdown("#### Top Cultural Sites Curated For You:")
        top_matches = recommend_by_interest(df_sites, user_input)
        st.markdown("<div style='display:flex; flex-direction:column; gap:24px;'>", unsafe_allow_html=True)
        for _, row in top_matches.iterrows():
            query = f"{row['SITE_NAME']} {row['STATE']}".replace(' ', '+')
            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={query}"
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; background:linear-gradient(90deg,#e6f9e6 70%,#fffbe6 100%); border-radius:12px; padding:14px 18px; margin-bottom:10px; min-height:100px; box-shadow:0 2px 8px #e0e0e0;">
                    <img src="{row['IMAGE_URL']}" style="width:140px; height:100px; object-fit:cover; border-radius:8px; margin-right:18px; border:2px solid #b7e4c7;">
                    <div style="flex:1;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.1em; color:#a63603; font-weight:700;">{row['SITE_NAME']}</span>
                            <span style="font-size:1em; color="#555;">({row['STATE']})</span>
                        </div>
                        <div style="font-size:0.97em; color:#333; margin:4px 0 0 0;">{row['DESCRIBTION']}</div>
                        <div style="margin-top:7px;">
                            <a href="https://www.google.com/search?q={query}" target="_blank" style="text-decoration:none;">
                                <button style="background:linear-gradient(90deg,#b7e4c7 60%,#ffe066 100%); color:#218838; border:none; border-radius:6px; padding:4px 12px; font-size:0.97em; display:flex; align-items:center; gap:7px; cursor:pointer; box-shadow:0 1px 4px #e0e0e0;">
                                    <i class="fab fa-google" style="color:#218838; font-size:1.1em;"></i>
                                    <span style="font-size:1em;">Explore More</span>
                                </button>
                            </a>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="margin-top:18px; font-size:1.05em; color:#444;">
            <b>Our AI matches your unique interests with India's most captivating cultural destinations.</b><br>
            <span style="color:#218838;">Let your curiosity lead the way – discover places you never knew existed!</span>
        </div>
        """, unsafe_allow_html=True)

# -------- Footer --------
st.markdown("""
<style>
.footer-bar {
    width: 100%;
    background: linear-gradient(90deg, #b7e4c7 60%, #ffe066 100%);
    box-shadow: 0 -2px 16px #e0e0e0;
    padding: 18px 0 10px 0;
    margin-top: 38px;
    display: flex;
    flex-direction: column;
    align-items: center;
    font-family: 'Segoe UI', Arial, sans-serif;
}
.footer-content {
    font-size: 1.18em;
    color: #000; /* changed to black */
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 7px;
    text-shadow: 0 1px 6px #ffe066;
}
.footer-icons {
    display: flex;
    gap: 22px;
    margin-top: 2px;
}
.footer-icons a {
    color: #218838 !important;
    font-size: 1.45em;
    transition: color 0.2s;
}
.footer-icons a:hover {
    color: #a63603 !important;
}
</style>
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

