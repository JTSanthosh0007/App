import os
import json
import streamlit as st

def verify_firebase_service_account():
    """
    Verify Firebase service account key configuration
    """
    st.title("Firebase Configuration Verification")
    
    # Possible key locations
    possible_paths = [
        os.path.join(os.getcwd(), "firebase-service-account.json"),
        os.path.expanduser("~/firebase-service-account.json")
    ]
    
    key_found = False
    key_path = None
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    key_data = json.load(f)
                
                # Validate key contents
                if key_data.get('project_id') == 'loginform-jt':
                    key_found = True
                    key_path = path
                    break
            except Exception as e:
                st.error(f"Error reading key at {path}: {e}")
    
    if key_found:
        st.success(f"✅ Firebase service account key found at: {key_path}")
        st.json(key_data)
    else:
        st.error("❌ Firebase service account key not found")
        st.markdown("""
        ### Setup Instructions
        1. Go to Firebase Console
        2. Select "loginform-jt" project
        3. Project Settings > Service Accounts
        4. Click "Generate new private key"
        5. Save the downloaded JSON file
        6. Rename to `firebase-service-account.json`
        7. Place in project root directory
        """)

def main():
    verify_firebase_service_account()

if __name__ == "__main__":
    main() 