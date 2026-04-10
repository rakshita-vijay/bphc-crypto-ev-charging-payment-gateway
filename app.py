"""
Streamlit Frontend for EV Charging Payment Gateway
Multi-page application with Grid Authority, Franchise, and EV Owner interfaces
"""

import streamlit as st
import os
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="EV Charging Payment Gateway",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'grid' not in st.session_state:
    from grid import Grid
    st.session_state.grid = Grid()

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("# ⚡ EV Charging Gateway")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    [
        "🏠 Home",
        "🏛️ Grid Authority",
        "🔌 Franchise/Kiosk",
        "🚗 EV Owner",
        "📊 Admin Analytics"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Users", len(st.session_state.grid.users))
with col2:
    st.metric("Franchises", len(st.session_state.grid.franchises))

st.sidebar.metric("Transactions", len(st.session_state.grid.blockchain))

# Route to pages
if page == "🏠 Home":
    from pages import home
    home.show()
elif page == "🏛️ Grid Authority":
    from pages import grid_authority
    grid_authority.show()
elif page == "🔌 Franchise/Kiosk":
    from pages import franchise_kiosk
    franchise_kiosk.show()
elif page == "🚗 EV Owner":
    from pages import ev_owner
    ev_owner.show()
elif page == "📊 Admin Analytics":
    from pages import admin_analytics
    admin_analytics.show()