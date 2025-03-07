import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
from logo import show_app_logo
from firebase_config import login_user, validate_email, send_password_reset_email

def init_auth_db():
    """Initialize authentication database"""
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, 
                  password TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def show_login_page():
    """
    Main login page with dynamic routing
    """
    # Determine which login-related page to show
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'
    
    # Show logo
    show_app_logo()
    
    # Routing for different login-related pages
    if st.session_state.current_page == 'login':
        handle_login()
    elif st.session_state.current_page == 'forgot_password':
        handle_forgot_password()

def show_signup_page():
    """Show the sign up page"""
    
    # Hide Streamlit elements
    st.markdown("""
        <style>
            header {display: none !important;}
            footer {display: none !important;}
            .block-container {padding-top: 1rem !important;}
            #MainMenu {visibility: hidden;}
            
            /* Form styling */
            .auth-form {
                background: #1a1a1a;
                padding: 2.5rem;
                border-radius: 12px;
                max-width: 400px;
                margin: 2rem auto;
            }
            .auth-header {
                text-align: center;
                margin-bottom: 2rem;
            }
            .auth-header h1 {
                color: white;
                font-size: 2.5rem;
                font-weight: 500;
            }
            .field-label {
                color: white;
                font-size: 1rem;
                margin-bottom: 0.5rem;
                font-weight: 400;
            }
            .name-fields {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
                margin-bottom: 1rem;
            }
            .stTextInput > div > div > input {
                background: #2d2d2d !important;
                border: 1px solid #404040 !important;
                color: #999 !important;
                font-size: 1rem !important;
                padding: 0.75rem !important;
                border-radius: 8px !important;
                height: 45px !important;
            }
            .stTextInput > div > div > input:focus {
                border-color: #666 !important;
                box-shadow: none !important;
                color: white !important;
            }
            .stButton > button {
                background: white !important;
                color: black !important;
                width: 100% !important;
                padding: 0.75rem !important;
                font-size: 1rem !important;
                font-weight: 500 !important;
                border: none !important;
                border-radius: 8px !important;
                margin-top: 1rem !important;
                height: 45px !important;
            }
            .stButton > button:hover {
                background: #f0f0f0 !important;
            }
            .divider {
                display: flex;
                align-items: center;
                text-align: center;
                margin: 1.5rem 0;
            }
            .divider::before, .divider::after {
                content: '';
                flex: 1;
                border-bottom: 1px solid #404040;
            }
            .divider span {
                color: #666;
                padding: 0 10px;
                font-size: 0.8rem;
                text-transform: uppercase;
            }
            .social-button {
                width: 100%;
                background: #2d2d2d;
                color: white;
                padding: 0.75rem;
                border: 1px solid #404040;
                border-radius: 8px;
                margin: 0.5rem 0;
                cursor: pointer;
                font-size: 1rem;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                height: 45px;
            }
            .social-button:hover {
                background: #363636;
            }
            .signin-text {
                color: #666;
                text-align: center;
                margin-top: 1.5rem;
                font-size: 0.9rem;
            }
            .signin-text a {
                color: #7c3aed;
                text-decoration: none;
                margin-left: 0.3rem;
            }
            .signin-text a:hover {
                text-decoration: underline;
            }
        </style>
        
        <div class="auth-form">
            <div class="auth-header">
                <h1>Sign up</h1>
            </div>
    """, unsafe_allow_html=True)
    
    # Name fields
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="field-label">First name</div>', unsafe_allow_html=True)
        first_name = st.text_input("", placeholder="Your first name", label_visibility="collapsed")
    
    with col2:
        st.markdown('<div class="field-label">Last name</div>', unsafe_allow_html=True)
        last_name = st.text_input("", placeholder="Your last name", label_visibility="collapsed")
    
    # Email field
    st.markdown('<div class="field-label">Email</div>', unsafe_allow_html=True)
    email = st.text_input("", placeholder="Your email address", label_visibility="collapsed", key="email")
    
    # Continue button
    if st.button("Continue"):
        if email and first_name and last_name:
            st.session_state.registration = {
                "email": email,
                "first_name": first_name,
                "last_name": last_name
            }
            st.rerun()
    else:
            st.error("Please fill in all fields")
    
    # OR divider
    st.markdown('<div class="divider"><span>or</span></div>', unsafe_allow_html=True)
    
    # Social login buttons
    st.markdown("""
        <button class="social-button">
            <img src="https://www.google.com/favicon.ico" style="width: 20px; height: 20px;">
            Continue with Google
        </button>
        <button class="social-button">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="white">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
            </svg>
            Continue with GitHub
        </button>
        <div class="signin-text">
            Already have an account? <a href="#">Sign in</a>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def register_user(username, password, email):
    """Register a new user"""
    try:
        conn = sqlite3.connect('auth.db')
        c = conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                 (username, hashed_pw, email))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def check_credentials(username, password):
    """Check if username/password combination is valid"""
    conn = sqlite3.connect('auth.db')
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
    result = c.fetchone()
    conn.close()
    return result is not None

def logout_user():
    """Log out the current user"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def handle_login():
    st.title("Login to Statement Analyzer")
    
    # Email input
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    # Login and Forgot Password columns
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Login", use_container_width=True):
            login_result = login_user(email, password)
            
            if login_result['success']:
                st.success("Login successful!")
                st.session_state.logged_in = True
                st.session_state.username = login_result.get('username', email.split('@')[0])
                st.session_state.user_id = login_result['user_id']
                st.session_state.current_page = 'platforms'
                st.rerun()
            else:
                st.error(login_result['error'])
    
    with col2:
        # Forgot Password button
        if st.button("Forgot Password?", use_container_width=True):
            st.session_state.current_page = 'forgot_password'
            st.rerun()

def handle_forgot_password():
    st.title("Reset Your Password")
    
    # Email input for password reset
    email = st.text_input("Enter your registered email")
    
    # Reset Password and Back to Login columns
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Send Reset Link", use_container_width=True):
            # Validate email
            if not email:
                st.error("Please enter your email address")
                return
            
            # Send password reset email
            try:
                reset_result = send_password_reset_email(email)
                
                if reset_result['success']:
                    st.success("Password reset link sent to your email!")
                    st.info("Check your inbox (and spam folder) for the reset link.")
                else:
                    st.error(reset_result['error'])
            
            except Exception as e:
                st.error(f"Error sending reset link: {str(e)}")
    
    with col2:
        if st.button("Back to Login", use_container_width=True):
            st.session_state.current_page = 'login'
            st.rerun()
    
    # Additional guidance
    st.markdown("""
    ### Password Reset Instructions
    1. Enter your registered email address
    2. Click "Send Reset Link"
    3. Check your email for the password reset instructions
    4. Follow the link to create a new password
    """)

def main():
    show_login_page()

if __name__ == "__main__":
    main()