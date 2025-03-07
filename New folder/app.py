import streamlit as st
from statement_parser import StatementParser
from auth import show_login_page, logout_user
from platforms.router import route_to_platform
from platforms.platform_select import show_platform_select
import time
import firebase_admin
from firebase_admin import credentials, auth
import pyrebase  # For additional Firebase functionality
from firebase_config import initialize_firebase, signup_user, login_user, send_password_reset_email

# Must be the first Streamlit command
st.set_page_config(
    page_title="Statement Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add global dark theme CSS
st.markdown("""
    <style>
    /* Global dark theme */
    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    /* Style for all containers */
    .stMarkdown, .stText, div[data-testid="stVerticalBlock"] {
        color: #ffffff;
    }
    
    /* Style for text inputs */
    .stTextInput input {
        background-color: #2d2d2d;
        color: #ffffff;
        border-color: #404040;
    }
    
    /* Style for buttons */
    .stButton button {
        background-color: #2d2d2d;
        color: #ffffff;
        border-color: #404040;
    }
    
    /* Style for success messages */
    .stSuccess {
        background-color: rgba(40, 167, 69, 0.2);
        color: #ffffff;
    }
    
    /* Style for error messages */
    .stError {
        background-color: rgba(220, 53, 69, 0.2);
        color: #ffffff;
    }
    
    /* Style for info messages */
    .stInfo {
        background-color: rgba(0, 123, 255, 0.2);
        color: #ffffff;
    }
    
    /* Style for warnings */
    .stWarning {
        background-color: rgba(255, 193, 7, 0.2);
        color: #ffffff;
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

def show_footer():
    """Show footer with all buttons"""
    footer = st.container()
    
    with footer:
        st.markdown(
            """
            <div class="footer">
                <div class="footer-buttons">
            """, 
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns([1, 1, 10])  # Removed one column, adjusted ratios
        
        with col1:
            if st.button("📞 Help"):
                st.session_state.show_support = True
                st.rerun()
        
        with col2:
            # Create placeholder for warning message
            warning_placeholder = st.empty()
            
            if st.button("🚪 Logout"):
                # Show warning message
                warning_placeholder.markdown(
                    """
                    <div class="warning-message">
                        ⚠️ Warning: Your session data will be permanently deleted in 5 seconds!
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Wait for 5 seconds with countdown
                for i in range(5, 0, -1):
                    warning_placeholder.markdown(
                        f"""
                        <div class="warning-message">
                            ⚠️ Warning: Your session data will be permanently deleted in {i} seconds!
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    time.sleep(1)
                
                # Clear warning message
                warning_placeholder.empty()
                
                # Perform logout
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def show_platform_selector_header():
    """Show platform selector in top right"""
    platforms = {
        'PhonePe': '📱',
        'Google Pay': '💳',
        'Paytm': '💰',
        'SuperMoney': '💸',
        'NAVI': '🏦',
        'Amazon Pay': '🛒',
        'WhatsApp Pay': '💬',
        'BHIM UPI': '🇮🇳',
        'Other': '🔄'
    }

    # Add CSS for platform selector
    st.markdown("""
        <style>
        /* Platform selector container */
        .platform-selector {
            position: fixed;
            top: 0;
            right: 0;
            padding: 15px;
            background-color: #1a1a1a;
            z-index: 1000;
            border-bottom-left-radius: 10px;
            box-shadow: -2px 2px 5px rgba(0,0,0,0.2);
        }
        
        /* Platform buttons grid */
        .platform-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            max-width: 400px;
        }
        
        /* Platform button style */
        .stButton button {
            width: 100%;
            background-color: #2d2d2d !important;
            border: 1px solid #404040 !important;
            color: #ffffff !important;
            padding: 10px !important;
            font-size: 14px !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton button:hover {
            background-color: #404040 !important;
            transform: translateY(-2px);
            box-shadow: 0 2px 5px rgba(255,255,255,0.1);
            border-color: #505050 !important;
        }
        
        .platform-active {
            background-color: #000000 !important;
            border-color: #505050 !important;
            color: #ffffff !important;
        }

        /* Make emojis more visible on dark background */
        .stButton button {
            text-shadow: 0 0 10px rgba(255,255,255,0.5);
        }
        </style>
    """, unsafe_allow_html=True)

    # Create platform selector container
    with st.container():
        st.markdown('<div class="platform-selector"><div class="platform-grid">', unsafe_allow_html=True)
        
        # Create columns for the grid
        cols = st.columns(3)
        current_platform = st.session_state.get('selected_platform', '')
        
        # Add platform buttons
        for idx, (platform, icon) in enumerate(platforms.items()):
            with cols[idx % 3]:
                if st.button(
                    f"{icon}\n{platform}",
                    key=f"platform_{platform}",
                    use_container_width=True,
                    type="secondary"
                ):
                    st.session_state.selected_platform = platform
                    st.rerun()
        
        st.markdown('</div></div>', unsafe_allow_html=True)

def main():
    # Initialize Firebase
    firebase, pyrebase_auth = initialize_firebase()

    # Initialize session state variables if they don't exist
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Initialize username with a default or empty string
    if 'username' not in st.session_state:
        st.session_state.username = ''

    # Initialize page state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'

    # Login Page
    if st.session_state.current_page == 'login':
        with st.container():
            st.title("Welcome to Statement Analyzer")
            
            # Custom CSS for login form
            st.markdown("""
                <style>
                .login-container {
                    max-width: 400px;
                    margin: 0 auto;
                    padding: 2rem;
                    background: #1a1a1a;
                    border-radius: 12px;
                }
                .login-buttons {
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                    margin-top: 1rem;
                }
                .forgot-password-link {
                    text-align: center;
                    color: #888;
                    margin-top: 1rem;
                    font-size: 0.9rem;
                }
                .forgot-password-link a {
                    color: #7c3aed;
                    text-decoration: none;
                    transition: color 0.3s ease;
                }
                .forgot-password-link a:hover {
                    color: #9333ea;
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            username = st.text_input("Email", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            # Checkbox for Terms and Conditions
            agree_terms = st.checkbox("I agree to the Terms and Conditions")

            # Display the link for Terms and Conditions
            st.markdown(
                "Click [here](https://yourwebsite.com/terms-and-conditions) to view the full Terms and Conditions.",
                unsafe_allow_html=True
            )

            # Login buttons container
            st.markdown('<div class="login-buttons">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Login", use_container_width=True):
                    if not agree_terms:
                        st.error("You must agree to the terms and conditions to log in.")
                    else:
                        # Use login_user function
                        login_result = login_user(username, password)
                        
                        if login_result['success']:
                            st.session_state.logged_in = True
                            st.session_state.username = login_result['username']
                            st.session_state.user_id = login_result['user_id']
                            st.session_state.current_page = 'platforms'
                            st.rerun()
                        else:
                            st.error(login_result['error'])
            
            with col2:
                if st.button("Sign Up", use_container_width=True):
                    # Switch to signup page
                    st.session_state.current_page = 'signup'
                    st.rerun()
            
            with col3:
                if st.button("Forgot Password", use_container_width=True):
                    # Switch to forgot password page
                    st.session_state.current_page = 'forgot_password'
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Signup Page
    elif st.session_state.current_page == 'signup':
        with st.container():
            st.title("Create an Account")
            
            # Custom CSS for signup form
            st.markdown("""
                <style>
                .signup-container {
                    max-width: 400px;
                    margin: 0 auto;
                    padding: 2rem;
                    background: #1a1a1a;
                    border-radius: 12px;
                }
                .signup-header {
                    text-align: center;
                    margin-bottom: 1.5rem;
                }
                .signup-buttons {
                    display: flex;
                    gap: 1rem;
                    margin-top: 1rem;
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="signup-container">', unsafe_allow_html=True)
            
            # Signup form fields
            new_username = st.text_input("Choose a Username", key="signup_username")
            new_email = st.text_input("Email Address", key="signup_email")
            new_password = st.text_input("Create Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
            
            # Signup and Back to Login buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Create Account", use_container_width=True):
                    if new_username and new_email and new_password:
                        if new_password == confirm_password:
                            # Use signup_user function
                            signup_result = signup_user(new_email, new_password, new_username)
                            
                            if signup_result['success']:
                                st.success("Account created successfully!")
                                st.session_state.logged_in = True
                                st.session_state.username = new_username
                                st.session_state.user_id = signup_result['user_id']
                                st.session_state.current_page = 'platforms'
                                st.rerun()
                            else:
                                st.error(signup_result['error'])
            with col2:
                if st.button("Back to Login", use_container_width=True):
                    st.session_state.current_page = 'login'
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Forgot Password Page
    elif st.session_state.current_page == 'forgot_password':
        with st.container():
            st.title("Reset Your Password")
            
            # Custom CSS for forgot password form
            st.markdown("""
                <style>
                .forgot-password-container {
                    max-width: 400px;
                    margin: 0 auto;
                    padding: 2rem;
                    background: #1a1a1a;
                    border-radius: 12px;
                }
                .password-reset-buttons {
                    display: flex;
                    gap: 1rem;
                    margin-top: 1rem;
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="forgot-password-container">', unsafe_allow_html=True)
            
            # Email input for password reset
            reset_email = st.text_input("Enter your registered email", key="reset_email")
            
            # Password reset buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Send Reset Link", use_container_width=True):
                    if reset_email:
                        # Call Firebase password reset function
                        reset_result = send_password_reset_email(reset_email)
                        
                        if reset_result['success']:
                            st.success("Password reset link sent to your email!")
                            # Optional: Add a delay or automatic return to login
                            time.sleep(2)
                            st.session_state.current_page = 'login'
                            st.rerun()
                        else:
                            st.error(reset_result['error'])
                    else:
                        st.warning("Please enter your email address")
            
            with col2:
                if st.button("Back to Login", use_container_width=True):
                    st.session_state.current_page = 'login'
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Logged in state
    else:
        # Show platform selection after login
        show_platform_select(st.session_state.username or "User")

if __name__ == "__main__":
    main() 