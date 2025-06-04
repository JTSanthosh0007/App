import streamlit as st
import hashlib
import re
import time
from supabase_config import (
    verify_email_exists,
    send_email,
    send_password_reset,
    create_new_user,
    validate_indian_phone,
    send_password_reset_email,
    send_login_code,
    update_subscription
)
from payment import show_subscription_plans
from utils import hide_streamlit_style
from statement_parser import StatementParser
from platforms.router import route_to_platform
from platforms.platform_select import show_platform_select
from firebase_auth import firebase_login, firebase_signup, firebase_send_password_reset, firebase_google_auth_url, handle_google_callback
import random
import string
from datetime import datetime
from functools import lru_cache
import concurrent.futures

# Must be the first Streamlit command
st.set_page_config(
    page_title="Statement Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import other modules after set_page_config
from utils import hide_streamlit_style
from statement_parser import StatementParser
from platforms.router import route_to_platform
from platforms.platform_select import show_platform_select

# Hide Streamlit style elements
#hide_st_style = """
#<style>
#MainMenu {visibility: hidden;}
#footer {visibility: hidden;}
#header {visibility: hidden;}
#</style>
#"""
#st.markdown(hide_st_style, unsafe_allow_html=True)

# Hide Streamlit's default UI elements
#hide_streamlit_style()

# Add global dark theme CSS
st.markdown("""
    <style>
    /* Global color variables */
    :root {
        --dark-gray: #1E1E1E;
        --soft-blue: #4A90E2;
        --white: #F5F5F5;
        --darker-gray: #171717;
        --light-blue: #5C9CE6;
        --background-dark: #1E1E1E;
        --surface-dark: #252525;
        --text-white: #F5F5F5;
        --text-gray: #A0A0A0;
    }

    /* Main background */
    .stApp {
        background-color: var(--background-dark);
    }

    /* Container styling */
    .login-container, .signup-container {
        background: var(--surface-dark);
        border: 1px solid #303030;
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.1);
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 12px;
    }

    /* Input fields */
    .stTextInput input, .stNumberInput input {
        background-color: var(--darker-gray) !important;
        border: 1px solid #303030 !important;
        color: var(--text-white) !important;
        border-radius: 6px !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--soft-blue) !important;
        box-shadow: 0 0 0 1px var(--soft-blue) !important;
    }

    /* Buttons */
    .stButton button {
        background-color: var(--soft-blue) !important;
        color: var(--white) !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
    }

    .stButton button:hover {
        background-color: var(--light-blue) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.2);
    }

    /* Secondary buttons */
    .stButton [data-baseweb="button"][kind="secondary"] {
        background-color: transparent !important;
        border: 1px solid var(--soft-blue) !important;
        color: var(--soft-blue) !important;
    }

    .stButton [data-baseweb="button"][kind="secondary"]:hover {
        background-color: rgba(74, 144, 226, 0.1) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--surface-dark);
        border-radius: 8px;
        padding: 4px;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: var(--text-gray);
        border-radius: 6px;
        padding: 8px 16px;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--soft-blue) !important;
        color: var(--white) !important;
        font-weight: 500 !important;
    }

    /* Headers */
    h1, h2, h3 {
        color: var(--white) !important;
    }

    /* Links */
    a {
        color: var(--soft-blue) !important;
        text-decoration: none !important;
    }

    a:hover {
        text-decoration: underline !important;
        color: var(--light-blue) !important;
    }

    /* Error messages */
    .stAlert {
        background-color: var(--surface-dark) !important;
        color: var(--text-white) !important;
        border: 1px solid #303030 !important;
    }

    /* Success messages */
    .element-container.success {
        background-color: rgba(74, 144, 226, 0.1) !important;
        border: 1px solid var(--soft-blue) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Add custom CSS for footer and buttons
st.markdown("""
    <style>
    /* Footer container */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #f8f9fa;
        padding: 20px 30px;  /* Even more padding */
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
        z-index: 999;
    }
    
    /* Button container within footer */
    .footer-buttons {
        display: flex;
        gap: 40px;  /* More gap between buttons */
        align-items: center;
    }
    
    /* Style for footer buttons */
    .footer .stButton button {
        background-color: transparent;
        border: none;
        color: #444;
        padding: 15px 30px !important;  /* Bigger padding */
        font-size: 18px !important;     /* Bigger font */
        cursor: pointer;
        transition: all 0.3s ease;
        min-width: 150px !important;    /* Bigger minimum width */
        border-radius: 10px;   /* More rounded corners */
        font-weight: 600;    /* Bolder text */
        height: auto !important;  /* Override Streamlit's default height */
        line-height: 1.5 !important;  /* Better text alignment */
    }
    
    .footer .stButton button:hover {
        color: #1f77b4;
        background-color: #e9ecef;
        transform: translateY(-3px);  /* Bigger lift effect */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Switch button specific style */
    .footer .stButton:first-child button {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    
    /* Help button specific style */
    .footer .stButton:nth-child(2) button {
        background-color: #e8f4f9;
        color: #0077b6;
        font-size: 20px !important;  /* Even bigger font for Help */
        font-weight: 600;
    }
    
    /* Logout button specific style */
    .footer .stButton:last-child button {
        background-color: #fff0f0;
        color: #dc3545;
        font-size: 20px !important;  /* Even bigger font for Logout */
        font-weight: 600;
    }
    
    /* Warning message above footer */
    .warning-message {
        position: fixed;
        bottom: 100px;  /* Adjusted for bigger footer */
        right: 20px;
        background-color: #FFF3CD;
        color: #856404;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #FFE69C;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: fadeIn 0.3s ease-in;
        font-size: 16px;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Hide Streamlit footer */
    footer {display: none;}
    
    /* Hide selectbox label */
    .stSelectbox label {display: none;}
    </style>
""", unsafe_allow_html=True)

# Add this to your existing CSS
st.markdown("""
    <style>
    /* Style for phone input */
    input[type="tel"] {
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        width: 100%;
    }
    
    /* Style for verification code input */
    input[type="text"][placeholder="Enter Verification Code"] {
        letter-spacing: 4px;
        font-size: 20px;
        text-align: center;
    }
    
    /* Style for tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #2d2d2d;
        border-radius: 4px;
        color: #ffffff;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #404040;
    }
    </style>
""", unsafe_allow_html=True)

# Update the error message styling to be smaller
st.markdown("""
    <style>
    /* Error message styling */
    .stAlert {
        background-color: rgba(255, 215, 0, 0.1) !important;
        border-left: 3px solid #FFD700 !important;  /* Thinner border */
        color: #FFD700 !important;
        padding: 0.5rem 0.75rem !important;  /* Reduced padding */
        margin: 0.5rem 0 !important;  /* Reduced margin */
        border-radius: 6px !important;  /* Smaller radius */
        font-size: 0.8rem !important;  /* Smaller font */
        display: flex !important;
        align-items: center !important;
        box-shadow: 0 2px 6px rgba(255, 215, 0, 0.15) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        max-width: 400px !important;  /* Limit width */
        margin-left: auto !important;  /* Center the alert */
        margin-right: auto !important;
    }

    /* Error icon */
    .stAlert:before {
        content: "⚠️";
        margin-right: 8px;  /* Reduced margin */
        font-size: 1rem !important;  /* Smaller icon */
    }

    /* Error message container */
    div[data-baseweb="notification"] {
        background-color: rgba(37, 37, 37, 0.9) !important;
        border: 1px solid #FFD700 !important;
        box-shadow: 0 2px 8px rgba(255, 215, 0, 0.2) !important;
        padding: 0.5rem !important;  /* Reduced padding */
    }

    /* Error text */
    .stAlert > div {
        color: #FFD700 !important;
        font-weight: 400 !important;  /* Slightly lighter weight */
        letter-spacing: 0.2px !important;
        line-height: 1.2 !important;  /* Tighter line height */
    }

    /* Error message animation */
    @keyframes slideIn {
        from { 
            transform: translateX(-5px);  /* Smaller slide */
            opacity: 0;
        }
        to { 
            transform: translateX(0);
            opacity: 1;
        }
    }

    .stAlert {
        animation: slideIn 0.2s ease-out;  /* Faster animation */
    }
    </style>
""", unsafe_allow_html=True)

# Update the background image in the CSS (fix indentation)
st.markdown("""
    <style>
    /* Background image for login page */
    .stApp {
        background: linear-gradient(rgba(30, 30, 30, 0.85), rgba(30, 30, 30, 0.85)),
                    url('https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Login container with glassmorphism effect */
    .login-container {
        background: rgba(37, 37, 37, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
        padding: 2rem !important;
        border-radius: 16px !important;
        max-width: 400px !important;
        margin: 2rem auto !important;
    }

    /* Title styling */
    .login-container h1 {
        color: #F5F5F5 !important;
        font-size: 2rem !important;
        margin-bottom: 2rem !important;
        text-align: center !important;
        font-weight: 500 !important;
    }

    /* Input fields with glassmorphism */
    .stTextInput input, .stNumberInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(5px) !important;
        -webkit-backdrop-filter: blur(5px) !important;
        color: #F5F5F5 !important;
        padding: 0.75rem 1rem !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: rgba(74, 144, 226, 0.5) !important;
        box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2) !important;
        background: rgba(255, 255, 255, 0.1) !important;
    }

    /* Button styling */
        .stButton button {
        background: linear-gradient(45deg, #4A90E2, #5C9CE6) !important;
        border: none !important;
        padding: 0.75rem 1rem !important;
        border-radius: 8px !important;
        color: white !important;
        font-weight: 500 !important;
        width: 100% !important;
        margin: 0.5rem 0 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3) !important;
        background: linear-gradient(45deg, #5C9CE6, #4A90E2) !important;
    }

    /* Secondary buttons */
    .stButton [data-baseweb="button"][kind="secondary"] {
        background: transparent !important;
        border: 1px solid rgba(74, 144, 226, 0.5) !important;
        color: #4A90E2 !important;
    }

    .stButton [data-baseweb="button"][kind="secondary"]:hover {
        background: rgba(74, 144, 226, 0.1) !important;
        border-color: #4A90E2 !important;
    }

    /* Hide fullscreen button and other Streamlit elements */
    .stApp > header {
        display: none !important;
    }

    #MainMenu {
        display: none !important;
    }

    footer {
        display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Add this new CSS for login header and subheader
st.markdown("""
    <style>
    .login-header {
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .login-subheader {
        font-size: 16px;
        color: #aaaaaa;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Cache database connection
@st.cache_resource(ttl=3600)
def get_database_connection():
    # Your database connection code here
    pass

# Cache user verification
@st.cache_data(ttl=300)  # Cache for 5 minutes
def verify_credentials_with_error_handling(email, hashed_password):
    try:
        return verify_email_exists(email, hashed_password)
    except Exception as e:
        st.error(f"Error verifying credentials: {str(e)}")
        return False

# Cache user creation
@st.cache_data(ttl=300)  # Cache for 5 minutes
def create_new_user_with_error_handling(email, username, password, phone):
    try:
        return create_new_user(email, username, password, phone)
    except Exception as e:
        st.error(f"Error creating user: {str(e)}")
        return False

# Optimize session state initialization
def initialize_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'recent_activity' not in st.session_state:
        st.session_state.recent_activity = []
    if 'current_platform' not in st.session_state:
        st.session_state.current_platform = None

# Cache data loading and processing
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_and_process_data(file_obj):
    parser = StatementParser(file_obj)
    return parser.parse()

# Optimize recent activity updates
@st.cache_data(ttl=300)  # Cache for 5 minutes
def update_recent_activity(bank_name, statement_name):
    try:
        activity = {
            'bank_name': bank_name,
            'statement_name': statement_name,
            'timestamp': datetime.now().isoformat()
        }
        if 'recent_activity' in st.session_state:
            st.session_state.recent_activity.insert(0, activity)
            # Keep only last 10 activities
            st.session_state.recent_activity = st.session_state.recent_activity[:10]
    except Exception as e:
        st.error(f"Error updating recent activity: {str(e)}")

# Optimize main function
def main():
    initialize_session_state()

    # Use columns for better layout performance
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.authenticated:
            show_login_page()
        else:
            show_main_content()

# Optimize login page
def show_login_page():
            st.title("Welcome to Statement Analyzer")
            
    # Use tabs for better performance
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_signup_form()

# Optimize main content display
def show_main_content():
    st.title("Statement Analyzer Dashboard")
    
    # Use tabs for better organization
    tab1, tab2, tab3 = st.tabs(["Upload Statement", "Recent Activity", "Settings"])
    
    with tab1:
        show_upload_section()
    
    with tab2:
        show_recent_activity()
    
    with tab3:
        show_settings()

def show_phonepe_analyzer():
    # Add a header row with back and logout buttons
    col_back, col_title, col_logout = st.columns([1, 2, 1])
    
    with col_back:
        if st.button("← Back", key="phonepe_back_btn"):
            st.session_state.current_page = 'dashboard'
            st.rerun()
    
    with col_title:
        st.title("PhonePe Statement Analyzer")
    
    with col_logout:
        if st.button("Logout", key="phonepe_logout_btn"):
            logout()
    
    # PhonePe statement upload section
    st.markdown("""
        <div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h3>Upload your PhonePe statement to analyze your transactions</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your PhonePe statement (PDF)", type="pdf", key="phonepe_uploader")
    
    if uploaded_file is not None:
        # Process the uploaded file
        with st.spinner("Analyzing your statement..."):
            # After successful analysis
            update_recent_activity("PhonePe", "Statement Analysis")

def show_recent_activity():
    """Display recent statement analysis activity"""
    st.markdown("""
        <h3 style='margin-bottom: 20px;'>Recent Activity</h3>
        <style>
        .activity-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            background: rgba(0,0,0,0.2);
            border-radius: 5px;
            overflow: hidden;
        }
        .activity-table th, .activity-table td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #333;
        }
        .activity-table th {
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-weight: 500;
        }
        .status-completed {
            color: #4CAF50;
            font-weight: 500;
        }
        .activity-table tr:hover {
            background: rgba(255,255,255,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize empty activity list if not exists
    if 'recent_activity' not in st.session_state:
        st.session_state.recent_activity = []

    if not st.session_state.recent_activity:
        st.info("No recent activity to show")
        return

    # Display the activity table
    activity_html = """
        <table class="activity-table">
            <tr>
                <th>Date</th>
                <th>Bank</th>
                <th>Statement</th>
                <th>Status</th>
            </tr>
    """
    
    for activity in st.session_state.recent_activity:
        activity_html += f"""
            <tr>
                <td>{activity['date']}</td>
                <td>{activity['bank']}</td>
                <td>{activity['statement']}</td>
                <td class="status-completed">{activity['status']}</td>
            </tr>
        """
    
    activity_html += "</table>"
    st.markdown(activity_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 