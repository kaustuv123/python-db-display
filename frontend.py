"""
Streamlit frontend — Population Dashboard.
Fetches data from FastAPI backend every 3 seconds and displays table, bar chart, and pie chart.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

API_URL = "http://localhost:8000/api/population"

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="World Population Dashboard",
    page_icon="🌍",
    layout="wide",
)

# ── Custom CSS for modern, minimal look ──────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Header */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .dashboard-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .dashboard-header p {
        margin: 0.3rem 0 0 0;
        opacity: 0.85;
        font-size: 0.95rem;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
        border: 1px solid #e2e6f5;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .metric-card .label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #6b7280;
        font-weight: 600;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #4338ca;
        margin-top: 0.2rem;
    }

    /* Section titles */
    .section-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #1e1b4b;
        margin-bottom: 0.5rem;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #e2e6f5;
    }

    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Hide the rerun / running overlay that causes dimming */
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    .stApp > div[data-testid="stAppViewBlockContainer"] {
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] > div {
        opacity: 1 !important;
    }
    .element-container, .stMarkdown, .stPlotlyChart, .stDataFrame {
        opacity: 1 !important;
        transition: none !important;
    }
    /* Prevent the script-running dimming */
    .appview-container .main .block-container {
        opacity: 1 !important;
    }
    div[data-testid="stScriptRunnerDialog"] {
        display: none !important;
    }

    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ── Fetch data ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=2)
def fetch_data():
    try:
        resp = requests.get(API_URL, timeout=5)
        resp.raise_for_status()
        return resp.json()["data"]
    except Exception:
        return None


data = fetch_data()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <h1>🌍 World Population Dashboard</h1>
    <p>Live data · Auto-refreshes every 3 seconds</p>
</div>
""", unsafe_allow_html=True)

if data is None:
    st.error("⚠️ Could not reach the backend. Make sure FastAPI is running on http://localhost:8000")
    st.stop()

df = pd.DataFrame(data)
df.rename(columns={"country": "Country", "population": "Population (M)", "updated_at": "Last Updated"}, inplace=True)

# ── Metric cards ─────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Total Countries</div>
        <div class="value">{len(df)}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Total Population</div>
        <div class="value">{df["Population (M)"].sum():,.0f}M</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Most Populated</div>
        <div class="value">{df.iloc[0]["Country"]}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Charts ───────────────────────────────────────────────────────────────────
chart_col1, chart_col2 = st.columns(2)

# Color palette
colors = px.colors.qualitative.Pastel

with chart_col1:
    st.markdown('<div class="section-title">📊 Population by Country</div>', unsafe_allow_html=True)
    fig_bar = px.bar(
        df,
        x="Country",
        y="Population (M)",
        color="Country",
        color_discrete_sequence=colors,
    )
    fig_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        showlegend=False,
        margin=dict(t=10, b=40, l=40, r=10),
        xaxis=dict(tickangle=-45),
        yaxis=dict(gridcolor="#eee"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    st.markdown('<div class="section-title">🥧 Population Share</div>', unsafe_allow_html=True)
    fig_pie = px.pie(
        df,
        names="Country",
        values="Population (M)",
        color_discrete_sequence=colors,
        hole=0.4,
    )
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(font=dict(size=10)),
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

# ── Data table ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Data Table</div>', unsafe_allow_html=True)
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Population (M)": st.column_config.NumberColumn(format="%d M"),
    },
)

# ── Auto-refresh every 3 seconds ────────────────────────────────────────────
time.sleep(3)
st.rerun()
