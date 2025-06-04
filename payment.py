import streamlit as st
import time
from supabase_config import update_subscription

def show_subscription_plans():
    st.title("Choose Your Plan")
    
    # Custom CSS for subscription cards
    st.markdown("""
        <style>
        .subscription-container {
            display: flex;
            justify-content: center;
            gap: 2rem;
            padding: 2rem;
        }
        .plan-card {
            background: #2d2d2d;
            border-radius: 15px;
            padding: 2rem;
            width: 300px;
            text-align: center;
            transition: transform 0.3s ease;
            border: 2px solid #404040;
        }
        .plan-card:hover {
            transform: translateY(-10px);
            border-color: #666;
        }
        .plan-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #ffffff;
        }
        .plan-price {
            font-size: 36px;
            color: #4CAF50;
            margin-bottom: 1rem;
        }
        .plan-features {
            text-align: left;
            margin: 1.5rem 0;
            color: #ddd;
        }
        .feature-item {
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create three columns for all plans
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="plan-card">
                <div class="plan-title">Basic Plan</div>
                <div class="plan-price">₹0<span style="font-size: 16px">/month</span></div>
                <div class="plan-features">
                    <div class="feature-item">✅ Basic Statement Analysis</div>
                    <div class="feature-item">✅ Transaction History</div>
                    <div class="feature-item">✅ Basic Reports</div>
                    <div class="feature-item">✅ Email Support</div>
                    <div class="feature-item">✅ Monthly Updates</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Get Started", key="free_plan", use_container_width=True):
            st.session_state.selected_plan = "free"
            success_placeholder = st.empty()
            success_placeholder.success("Plan selected! Redirecting...")
            time.sleep(2)
            success_placeholder.empty()
            st.session_state.current_page = 'platforms'
            st.rerun()

    with col2:
        st.markdown("""
            <div class="plan-card" style="position: relative;">
                <div class="popular-tag">POPULAR</div>
                <div class="plan-title">Premium</div>
                <div class="plan-price">₹299<span style="font-size: 16px">/month</span></div>
                <div class="plan-features">
                    <div class="feature-item">✅ Advanced Statement Analysis</div>
                    <div class="feature-item">✅ Unlimited Transactions</div>
                    <div class="feature-item">✅ Detailed Reports</div>
                    <div class="feature-item">✅ Priority Email Support</div>
                    <div class="feature-item">✅ Advanced Analytics</div>
                    <div class="feature-item">✅ AI-Powered Analysis</div>
                    <div class="feature-item">❌ AI Financial Recommendations</div>
                </div>
                <div class="development-badge">Under Development</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Coming Soon", key="premium_plan", type="secondary", use_container_width=True):
            st.info("🔧 Premium Plan is currently under development. We're working hard to bring you advanced AI-powered features!", icon="⚡")
            time.sleep(3)
            st.rerun()

    with col3:
        st.markdown("""
            <div class="plan-card">
                <div class="plan-title">Prime Plus</div>
                <div class="plan-price">₹499<span style="font-size: 16px">/month</span></div>
                <div class="plan-features">
                    <div class="feature-item">✅ Everything in Premium</div>
                    <div class="feature-item">✅ AI Financial Recommendations</div>
                    <div class="feature-item">✅ Smart Money Management</div>
                    <div class="feature-item">✅ Investment Insights</div>
                    <div class="feature-item">✅ Personalized Savings Goals</div>
                    <div class="feature-item">✅ Custom Reports</div>
                </div>
                <div style="margin-top: 1rem; padding: 1rem; background: rgba(76, 175, 80, 0.1); border-radius: 10px;">
                    <span style="color: #4CAF50; font-weight: bold;">🤖 AI-Powered Features:</span>
                    <ul style="list-style: none; padding-left: 0; margin-top: 0.5rem;">
                        <li>• Smart Budget Planning</li>
                        <li>• Expense Predictions</li>
                        <li>• Investment Recommendations</li>
                        <li>• Spending Pattern Analysis</li>
                    </ul>
                </div>
                <div class="development-badge">Under Development</div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Coming Soon", key="prime_plus_plan", type="secondary", use_container_width=True):
            st.info("🔧 Prime Plus Plan is currently under development. We're crafting advanced AI features for smarter financial insights!", icon="💡")
            time.sleep(3)
            st.rerun()

    # Add CSS for development badge
    st.markdown("""
        <style>
        .development-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255, 152, 0, 0.9);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

def show_payment_options(plan_name, amount):
    st.session_state.payment_page = True
    st.session_state.plan_name = plan_name
    st.session_state.amount = amount
    
    st.markdown("""
        <style>
        .payment-container {
            max-width: 500px;
            margin: 2rem auto;
            padding: 2rem;
            background: #2d2d2d;
            border-radius: 15px;
        }
        
        .payment-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .payment-method {
            margin: 1rem 0;
            padding: 1rem;
            border: 1px solid #404040;
            border-radius: 10px;
            cursor: pointer;
        }
        
        .payment-method:hover {
            background: #404040;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="payment-container">
            <div class="payment-header">
                <h2>Payment for {plan_name}</h2>
                <p>Amount: ₹{amount}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    payment_method = st.selectbox(
        "Select Payment Method",
        ["Credit/Debit Card", "UPI", "Net Banking", "Wallet"]
    )
    
    if payment_method == "Credit/Debit Card":
        st.text_input("Card Number")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Expiry Date")
        with col2:
            st.text_input("CVV")
        st.text_input("Card Holder Name")
    
    elif payment_method == "UPI":
        st.text_input("UPI ID")
    
    elif payment_method == "Net Banking":
        st.selectbox("Select Bank", ["SBI", "HDFC", "ICICI", "Axis", "Other"])
    
    elif payment_method == "Wallet":
        st.selectbox("Select Wallet", ["Paytm", "PhonePe", "Google Pay", "Amazon Pay"])
    
    if st.button("Pay Now"):
        # Here you would integrate with your payment gateway
        st.success("Payment successful! Updating subscription...")
        if handle_subscription_update(st.session_state.user_id, st.session_state.selected_plan):
            st.success("Subscription updated successfully!")
            time.sleep(2)
            st.session_state.current_page = 'platforms'
            st.rerun()
        else:
            st.error("Failed to update subscription. Please contact support.")
    
    if st.button("Back to Plans"):
        st.session_state.payment_page = False
        st.rerun()

def handle_subscription_update(user_id, plan_type):
    """
    Handle subscription update after payment
    """
    try:
        result = update_subscription(user_id, plan_type)
        return result["success"]
    except Exception as e:
        st.error(f"Error updating subscription: {str(e)}")
        return False

def show_coming_soon_page(plan_name):
    st.markdown("""
        <style>
        .coming-soon-container {
            text-align: center;
            padding: 3rem;
            max-width: 600px;
            margin: 2rem auto;
            background: rgba(45, 45, 45, 0.9);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        .coming-soon-title {
            font-size: 2.5rem;
            color: #4CAF50;
            margin-bottom: 1rem;
        }
        .coming-soon-text {
            font-size: 1.2rem;
            color: #ddd;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        .notify-input {
            max-width: 300px;
            margin: 0 auto;
        }
        .launch-date {
            margin: 2rem 0;
            padding: 1rem;
            background: rgba(76, 175, 80, 0.1);
            border-radius: 10px;
            color: #4CAF50;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="coming-soon-container">
            <div class="coming-soon-title">🚀 Coming Soon!</div>
            <div class="coming-soon-text">
                Our {plan_name} is under development and will be launching soon with 
                exciting AI-powered features to revolutionize your financial analysis.
            </div>
            <div class="launch-date">
                Expected Launch: March 2024
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Notification signup
    st.markdown('<div class="notify-input">', unsafe_allow_html=True)
    email = st.text_input("Get notified when we launch:", placeholder="Enter your email")
    if st.button("Notify Me", use_container_width=True):
        if email:
            # Here you would add the email to your notification list
            st.success("Thanks! We'll notify you when we launch.")
            time.sleep(2)
            st.session_state.current_page = 'platforms'
            st.rerun()
        else:
            st.warning("Please enter your email address")
    st.markdown('</div>', unsafe_allow_html=True)

    # Back button
    if st.button("← Back to Plans", use_container_width=False):
        st.session_state.current_page = 'payment'
        st.rerun()
