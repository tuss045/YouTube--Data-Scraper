import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import re
from io import BytesIO
from datetime import date, timedelta

st.set_page_config(
    page_title="VidIQ Nova — YouTube Analytics",
    page_icon="🤖",
    layout="wide"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Page background */
.stApp {
    background: linear-gradient(135deg, #0a081a, #161233, #111124);
    min-height: 100vh;
}

/* Hide default streamlit header */
header[data-testid="stHeader"] { background: transparent; }

/* Hero banner */
.hero {
    background: linear-gradient(120deg, #121026 0%, #171b3a 50%, #0d2347 100%);
    border: 1px solid rgba(229, 57, 53, 0.25);
    border-radius: 20px;
    padding: 2.2rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(229,57,53,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 0.3rem;
    letter-spacing: -0.5px;
}
.hero-title span {
    color: #e53935;
}
.hero-sub {
    font-size: 1rem;
    color: rgba(255,255,255,0.6);
    margin: 0;
}

/* Section headers */
.section-head {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.45);
    margin-bottom: 0.6rem;
    margin-top: 1rem;
}

/* Metric cards */
.metric-row {
    display: flex;
    gap: 14px;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.metric-card {
    flex: 1;
    min-width: 160px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.2rem;
    transition: transform 0.2s, border-color 0.2s;
}
.metric-card:hover {
    border-color: rgba(255,255,255,0.15);
}
.metric-card .m-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.4);
    margin-bottom: 6px;
}
.metric-card .m-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
}
.metric-card .m-sub {
    font-size: 0.72rem;
    color: rgba(255,255,255,0.3);
    margin-top: 6px;
}
.metric-card.red { border-color: rgba(229, 57, 53, 0.3); background: rgba(229, 57, 53, 0.02); }
.metric-card.red .m-value { color: #ff7373; }
.metric-card.blue { border-color: rgba(66, 165, 245, 0.3); background: rgba(66, 165, 245, 0.02); }
.metric-card.blue .m-value { color: #64b5f6; }
.metric-card.green { border-color: rgba(102, 187, 106, 0.3); background: rgba(102, 187, 106, 0.02); }
.metric-card.green .m-value { color: #81c784; }
.metric-card.purple { border-color: rgba(156, 39, 176, 0.3); background: rgba
