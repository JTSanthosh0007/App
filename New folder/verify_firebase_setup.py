import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth

def check_firebase_setup():
    """
    Comprehensive Firebase setup verification
    """
    st.title("Firebase Configuration Verification")

    # Check Firebase Admin SDK initialization
    try:
        # Attempt to get the default app
        default_app = firebase_admin.get_app()
        st.success("✅ Firebase Admin SDK Initialized Successfully")
        
        # Additional app details
        st.write("App Name:", default_app.name)
        st.write("Project ID:", default_app.project_id)
    
    except ValueError:
        st.error("❌ Firebase Admin SDK Not Initialized")
        st.markdown("""
        ### Setup Instructions
        1. Download service account key from Firebase Console
        2. Rename to `firebase-service-account.json`
        3. Place in project root directory
        """)

    # Check authentication capabilities
    try:
        # Attempt a simple auth operation (list users)
        # Note: This might require specific permissions
        users = list(auth.users_from_project('loginform-jt'))
        st.success(f"✅ Authentication Configured (Total Users: {len(users)})")
    
    except Exception as e:
        st.warning("⚠️ Authentication verification failed")
        st.error(str(e))

def main():
    check_firebase_setup()

if __name__ == "__main__":
    main() 