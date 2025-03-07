import streamlit as st
from .phonepe import show_phonepe_page
from .googlepay import show_googlepay_page
from .paytm import show_paytm_page
from .supermoney import show_supermoney_page
from support import show_support_form
import time

def show_platform_grid():
    """Show all platforms in a grid layout"""
    st.markdown("""
        <style>
        .platform-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
            gap: 0.5rem;
            padding: 0.5rem;
            margin-top: 1rem;
        }
        .platform-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 0.5rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .platform-card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.1);
        }
        .platform-icon {
            font-size: 1.5rem;
            margin-bottom: 0.3rem;
        }
        .platform-name {
            color: #ffffff;
            font-size: 0.8rem;
        }
        .active-platform {
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .stButton button {
            padding: 0.3rem 0.5rem !important;
            font-size: 0.8rem !important;
            min-height: 0px !important;
            height: auto !important;
            width: 100%;
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: none !important;
            margin: 0 !important;
        }
        .stButton button:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
            transform: translateY(-1px);
        }
        .utility-buttons {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
            justify-content: center;
        }
        .help-button button {
            background-color: rgba(0, 123, 255, 0.1) !important;
            color: #0077ff !important;
        }
        .logout-button button {
            background-color: rgba(255, 59, 48, 0.1) !important;
            color: #ff3b30 !important;
        }
        .back-button {
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1000;
        }
        .back-button button {
            background-color: rgba(255,255,255,0.1) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            color: white !important;
            padding: 0.5rem 1rem !important;
        }
        .back-button button:hover {
            background-color: rgba(255,255,255,0.2) !important;
            border-color: rgba(255,255,255,0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    platforms = {
        'PhonePe': '📱',
        'Paytm': '💰',
        'SuperMoney': '💸',
        'Google Pay': '💳',
        'Amazon Pay': '🛒',
        'BHIM': '🇮🇳',
        'WhatsApp Pay': '💬',
        'Other': '🔄'
    }

    # Remove currently selected platform from the grid
    current_platform = st.session_state.get('selected_platform')
    if current_platform:
        platforms_to_show = {k: v for k, v in platforms.items() if k != current_platform}
    else:
        platforms_to_show = platforms

    st.markdown('<div class="platform-grid">', unsafe_allow_html=True)
    
    # Calculate number of columns based on remaining platforms
    num_platforms = len(platforms_to_show)
    num_cols = min(6, num_platforms)  # Use fewer columns if fewer platforms
    cols = st.columns(num_cols)
    
    for idx, (platform, icon) in enumerate(platforms_to_show.items()):
        with cols[idx % num_cols]:
            active_class = "active-platform" if platform == st.session_state.get('selected_platform', '') else ""
            if st.button(f"{icon}\n{platform}", key=f"btn_{platform}", use_container_width=True):
                st.session_state.selected_platform = platform
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add Help and Logout buttons
    st.markdown('<div class="utility-buttons">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📞 Help", key="help_button", use_container_width=True):
            st.session_state.show_support = True
            st.rerun()
            
    with col2:
        warning_placeholder = st.empty()
        
        if st.button("🚪 Logout", key="logout_button", use_container_width=True):
            warning_placeholder.warning("⚠️ Logging out in 3 seconds...")
            time.sleep(1)
            warning_placeholder.warning("⚠️ Logging out in 2 seconds...")
            time.sleep(1)
            warning_placeholder.warning("⚠️ Logging out in 1 second...")
            time.sleep(1)
            warning_placeholder.empty()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

def route_to_platform(platform_name, username):
    """Route to appropriate platform page"""
    try:
        # Clear everything
        st.empty()
        
        # Back button with styling
        st.markdown("""
            <style>
            .back-button {
                position: fixed;
                top: 0.5rem;
                left: 1rem;
                z-index: 1000;
            }
            .back-button button {
                background-color: rgba(30,30,30,0.9) !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
                color: #cccccc !important;
                padding: 0.4rem 1rem !important;
                font-size: 0.9rem !important;
                border-radius: 0.5rem !important;
            }
            .back-button button:hover {
                background-color: rgba(40,40,40,0.9) !important;
                border-color: rgba(255,255,255,0.2) !important;
                color: white !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Back button in a clean container
        with st.container():
            st.markdown('<div class="back-button">', unsafe_allow_html=True)
            if st.button("← Back to Platforms"):
                del st.session_state.selected_platform
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Route to appropriate platform
        if platform_name == 'PhonePe':
            show_phonepe_page(username)
        elif platform_name in ['Paytm UPI', 'Paytm']:
            show_paytm_page(username)
        else:
            st.info(f"Support for {platform_name} is coming soon!")
            
    except Exception as e:
        st.error(f"Error analyzing statement: {str(e)}")
        st.error("Please make sure you're uploading a valid statement file.") 