"""
SevaSaathi - Main Application
Entry point for the Streamlit application
"""

import streamlit as st
import os
from dotenv import load_dotenv

from config.settings import PAGE_CONFIG, GEMINI_API_URL, GENERATION_CONFIG
from ui.styles import apply_custom_styles
from ui.pages import (
    render_main_page,
    render_schemes_page,
    render_profile_page,
    render_search_page,
    render_about_page,
    render_statistics_page,
    render_settings_page
)
from utils.data_loader import initialize_session_state, load_schemes_data

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Chatbot", page_icon="🤖")

# Optionally apply custom styles if defined
try:
    apply_custom_styles()
except Exception:
    pass

def main():
    # Initialize session state
    initialize_session_state()

    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        (
            "Home",
            "Eligible Schemes",
            "Profile",
            "Search Schemes",
            "Statistics",
            "Settings",
            "About"
        )
    )

    if page == "Home":
        st.markdown('<h1 style="color: green;">🤖 SevaSaathi</h1>', unsafe_allow_html=True)
        render_main_page()
    elif page == "Eligible Schemes":
        eligible_schemes = st.session_state.get('last_eligible_schemes', [])
        render_schemes_page(eligible_schemes)
    elif page == "Profile":
        render_profile_page()
    elif page == "Search Schemes":
        render_search_page()
    elif page == "Statistics":
        render_statistics_page()
    elif page == "Settings":
        render_settings_page()
    elif page == "About":
        render_about_page()
    else:
        st.markdown('<h1 style="color: green;">SevaSaathi</h1>', unsafe_allow_html=True)
        render_main_page()

if __name__ == "__main__":
    main()