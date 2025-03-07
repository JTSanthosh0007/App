import streamlit as st
from platforms.router import route_to_platform

def display_grid(platforms):
    """Helper function to display platforms in a grid"""
    cols = st.columns(8)
    for idx, (platform, details) in enumerate(platforms.items()):
        with cols[idx % 8]:
            if st.button(
                f"{details['icon']}\n{platform}\n{details['status']}", 
                key=f"{details['category']}_{platform}",
                use_container_width=True,
                disabled=details['status'] != 'Available'
            ):
                st.session_state.selected_platform = platform
                route_to_platform(platform, st.session_state.username)
                return

def show_platform_select(username):
    # If a platform is selected, route to it and return immediately
    if 'selected_platform' in st.session_state:
        route_to_platform(st.session_state.selected_platform, username)
        return

    # Only show the platform selection if no platform is selected
    st.title(f"Welcome {username}! 👋")
    st.markdown("Select your preferred payment method to analyze statements")
    
    # Add custom CSS
    st.markdown("""
        <style>
        .platform-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
            gap: 0.5rem;
            padding: 0.75rem;
            background: #000000;
        }
        .platform-card {
            background: #111111;
            border-radius: 6px;
            padding: 0.5rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 1px solid #333333;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }
        .platform-card:hover {
            transform: translateY(-3px);
            background: #222222;
            border-color: #ffffff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .platform-icon {
            font-size: 1.5rem;
            margin-bottom: 0.25rem;
            filter: grayscale(100%);
            transition: all 0.3s ease;
        }
        .platform-name {
            color: #ffffff;
            font-size: 0.7rem;
            font-weight: 500;
            margin-bottom: 0.2rem;
        }
        .platform-status {
            font-size: 0.6rem;
            color: #888888;
            margin-top: 0.2rem;
        }
        .status-available {
            color: #00ff00;
        }
        .status-coming-soon {
            color: #888888;
        }
        .category-header {
            color: #ffffff;
            font-size: 1rem;
            font-weight: 600;
            margin: 1rem 0 0.5rem 0;
            padding-bottom: 0.3rem;
            border-bottom: 1px solid #333333;
        }
        .stButton button {
            background-color: #222222;
            color: white;
            border: 1px solid #333333;
            padding: 0.4rem;
            text-align: center;
            transition: all 0.2s ease;
            height: auto;
            white-space: pre-wrap;
            font-size: 0.65rem;
            min-height: 0;
            line-height: 1.2;
        }
        .stButton button:hover:not([disabled]) {
            transform: translateY(-2px);
            background-color: #333333;
            border-color: white;
        }
        .stButton button[disabled] {
            opacity: 0.6;
            cursor: not-allowed;
        }
        </style>
    """, unsafe_allow_html=True)

    # Add search box
    search = st.text_input(
        "🔍 Search for your bank or payment platform",
        key="platform_search",
        help="Type to search for any bank or payment platform"
    )

    # Update the all_platforms dictionary to show only PhonePe and Paytm as available
    all_platforms = {
        # UPI Platforms - Only PhonePe and Paytm are available
        'Paytm UPI': {'icon': '💰', 'status': 'Available', 'category': 'UPI'},
        'PhonePe': {'icon': '📱', 'status': 'Available', 'category': 'UPI'},
        'Google Pay': {'icon': '💳', 'status': 'Coming Soon', 'category': 'UPI'},
        'BHIM': {'icon': '🇮🇳', 'status': 'Coming Soon', 'category': 'UPI'},
        'WhatsApp Pay': {'icon': '💬', 'status': 'Coming Soon', 'category': 'UPI'},
        'Amazon Pay': {'icon': '🛒', 'status': 'Coming Soon', 'category': 'UPI'},
        
        # Public Sector Banks - All set to Coming Soon
        'State Bank of India': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Public Sector Bank'},
        'Bank of Baroda': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Public Sector Bank'},
        'Bank of India': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Public Sector Bank'},
        'Bank of Maharashtra': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Public Sector Bank'},
        'Canara Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Public Sector Bank'},
        'Central Bank of India': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Public Sector Bank'},
        'Indian Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Public Sector Bank'},
        'Indian Overseas Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Public Sector Bank'},
        'Punjab & Sind Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Public Sector Bank'},
        'Punjab National Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Public Sector Bank'},
        'UCO Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Public Sector Bank'},
        'Union Bank of India': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Public Sector Bank'},

        # Private Sector Banks - All set to Coming Soon
        'Axis Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'Bandhan Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'CSB Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'City Union Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'DCB Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'Dhanlaxmi Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'Federal Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'HDFC Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'ICICI Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'IDBI Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'IDFC First Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'IndusInd Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'Jammu & Kashmir Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'Karnataka Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'Karur Vysya Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'Kotak Mahindra Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'Nainital Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'RBL Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'South Indian Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'Tamilnad Mercantile Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},
        'YES Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Private Sector Bank'},

        # Small Finance Banks - All set to Coming Soon
        'AU Small Finance Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Small Finance Bank'},
        'Capital Small Finance Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Small Finance Bank'},
        'Equitas Small Finance Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Small Finance Bank'},
        'ESAF Small Finance Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Small Finance Bank'},
        'Suryoday Small Finance Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Small Finance Bank'},
        'Ujjivan Small Finance Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Small Finance Bank'},
        'Utkarsh Small Finance Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Small Finance Bank'},
        'North East Small Finance Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Small Finance Bank'},
        'Jana Small Finance Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Small Finance Bank'},
        'Shivalik Small Finance Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Small Finance Bank'},
        'Unity Small Finance Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Small Finance Bank'},

        # Payment Banks - All set to Coming Soon
        'Airtel Payments Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Payment Bank'},
        'India Post Payments Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Payment Bank'},
        'FINO Payments Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Payment Bank'},
        'Paytm Payments Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Payment Bank'},
        'Jio Payments Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Payment Bank'},
        'NSDL Payments Bank': {'icon': '🏦', 'status': 'Coming Soon', 'category': 'Payment Bank'},
    }

    # Filter platforms based on search
    if search:
        search = search.lower()
        filtered_platforms = {
            name: details for name, details in all_platforms.items()
            if search in name.lower() or search in details['category'].lower()
        }
        
        if filtered_platforms:
            st.markdown('<div class="category-header">🔍 Search Results</div>', unsafe_allow_html=True)
            
            # Display search results in grid
            cols = st.columns(6)
            for idx, (platform, details) in enumerate(filtered_platforms.items()):
                with cols[idx % 6]:
                    if st.button(
                        f"{details['icon']}\n{platform}\n{details['status']}", 
                        key=f"search_{platform}",
                        use_container_width=True,
                        disabled=details['status'] != 'Available'
                    ):
                        st.session_state.selected_platform = platform
                        route_to_platform(platform, username)
                        return
        else:
            st.info("No platforms found matching your search. Try a different term.")
            
    # If no search or showing all results
    if not search:
        # Group platforms by category
        upi_platforms = {k: v for k, v in all_platforms.items() if v['category'] == 'UPI'}
        public_banks = {k: v for k, v in all_platforms.items() if v['category'] == 'Public Sector Bank'}
        private_banks = {k: v for k, v in all_platforms.items() if v['category'] == 'Private Sector Bank'}
        small_finance_banks = {k: v for k, v in all_platforms.items() if v['category'] == 'Small Finance Bank'}
        payment_banks = {k: v for k, v in all_platforms.items() if v['category'] == 'Payment Bank'}

        # Display UPI Platforms
        st.markdown('<div class="category-header">🔄 UPI Payment Apps</div>', unsafe_allow_html=True)
        display_grid(upi_platforms)

        # Display Public Sector Banks
        st.markdown('<div class="category-header">🏦 Public Sector Banks</div>', unsafe_allow_html=True)
        display_grid(public_banks)

        # Display Private Sector Banks
        st.markdown('<div class="category-header">🏛️ Private Sector Banks</div>', unsafe_allow_html=True)
        display_grid(private_banks)

        # Display Small Finance Banks
        st.markdown('<div class="category-header">💰 Small Finance Banks</div>', unsafe_allow_html=True)
        display_grid(small_finance_banks)

        # Display Payment Banks
        st.markdown('<div class="category-header">💳 Payment Banks</div>', unsafe_allow_html=True)
        display_grid(payment_banks)

    # Add custom CSS for buttons
    st.markdown("""
        <style>
        .stButton button {
            background-color: #222222;
            color: white;
            border: 1px solid #333333;
            padding: 1rem;
            text-align: center;
            transition: all 0.3s ease;
            height: auto;
            white-space: pre-wrap;
        }
        .stButton button:hover:not([disabled]) {
            transform: translateY(-5px);
            background-color: #333333;
            border-color: white;
        }
        .stButton button[disabled] {
            opacity: 0.6;
            cursor: not-allowed;
        }
        </style>
    """, unsafe_allow_html=True) 