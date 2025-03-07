import streamlit as st

def show_app_logo():
    """
    Display the Statement Analyzer logo with custom styling
    """
    st.markdown("""
    <style>
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #5f27cd, #341f97);
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .logo-text {
        font-family: 'Arial Black', sans-serif;
        font-size: 2.5rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-left: 1rem;
    }
    .logo-icon {
        font-size: 3rem;
        margin-right: 1rem;
    }
    </style>
    
    <div class="logo-container">
        <div class="logo-icon">📊</div>
        <div class="logo-text">Statement Analyzer</div>
    </div>
    """, unsafe_allow_html=True)

def show_phonepe_logo():
    """
    Display the PhonePe Statement Analyzer specific logo with advanced styling and animations
    """
    st.markdown("""
    <style>
    .phonepe-logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);  /* Enhanced gradient */
        border-radius: 20px;
        box-shadow: 
            0 10px 20px rgba(0,0,0,0.2), 
            0 6px 6px rgba(0,0,0,0.1);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        perspective: 1000px;
        overflow: hidden;
        position: relative;
    }
    .phonepe-logo-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(
            circle at center, 
            rgba(255,255,255,0.1) 0%, 
            rgba(255,255,255,0) 70%
        );
        transform: rotate(-45deg);
        opacity: 0.3;
        transition: all 0.5s ease;
    }
    .phonepe-logo-container:hover::before {
        transform: rotate(0deg);
        opacity: 0.5;
    }
    .phonepe-logo-container:hover {
        transform: scale(1.03) rotateX(5deg) rotateY(-5deg);
        box-shadow: 
            0 15px 30px rgba(0,0,0,0.3), 
            0 10px 10px rgba(0,0,0,0.2);
    }
    .phonepe-logo-icon {
        font-size: 4.5rem;
        margin-right: 1.5rem;
        color: #ffffff;
        text-shadow: 
            0 0 10px rgba(255,255,255,0.3), 
            2px 2px 4px rgba(0,0,0,0.3);
        animation: 
            pulse 3s infinite cubic-bezier(0.4, 0, 0.2, 1),
            float 4s infinite ease-in-out;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    .phonepe-logo-text {
        font-family: 'Arial Black', sans-serif;
        display: flex;
        flex-direction: column;
        position: relative;
    }
    .phonepe-logo-main {
        font-size: 3.2rem;
        color: white;
        line-height: 1.2;
        text-shadow: 
            2px 2px 4px rgba(0,0,0,0.3),
            0 0 10px rgba(255,255,255,0.2);
        letter-spacing: -1px;
    }
    .phonepe-logo-sub {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.8);
        margin-top: 0.5rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        opacity: 0.8;
        transition: all 0.3s ease;
    }
    .phonepe-logo-container:hover .phonepe-logo-sub {
        letter-spacing: 3px;
        opacity: 1;
    }
    </style>
    
    <div class="phonepe-logo-container">
        <div class="phonepe-logo-icon">📱</div>
        <div class="phonepe-logo-text">
            <div class="phonepe-logo-main">PhonePe</div>
            <div class="phonepe-logo-sub">Statement Analyzer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_paytm_logo():
    """
    Display the Paytm Statement Analyzer specific logo
    """
    st.markdown("""
    <style>
    .paytm-logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #4a4a4a, #2c3e50);
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    .paytm-logo-icon {
        font-size: 3.5rem;
        margin-right: 1.5rem;
        color: #00baf2;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .paytm-logo-text {
        font-family: 'Arial Black', sans-serif;
        font-size: 2.8rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        display: flex;
        flex-direction: column;
    }
    .paytm-logo-main {
        line-height: 1.2;
        color: #00baf2;
    }
    .paytm-logo-sub {
        font-size: 1rem;
        color: #e0e0e0;
        margin-top: 0.3rem;
    }
    </style>
    
    <div class="paytm-logo-container">
        <div class="paytm-logo-icon">💰</div>
        <div class="paytm-logo-text">
            <div class="paytm-logo-main">Paytm</div>
            <div class="paytm-logo-sub">Statement Analyzer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
