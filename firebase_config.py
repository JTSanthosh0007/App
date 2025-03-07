import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
import re

def get_absolute_path(relative_path):
    """
    Convert relative path to absolute path
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(base_dir, relative_path))

def initialize_firebase():
    """
    Initialize Firebase with secure configuration
    """
    try:
        # Determine the absolute path to the service account file
        service_account_path = get_absolute_path("firebase-service-account.json")
        
        # Validate service account key
        if not os.path.exists(service_account_path):
            st.error(f"Firebase service account file not found at: {service_account_path}")
            return None, None

        # Use Streamlit secrets for configuration
        firebase_config = {
            "apiKey": st.secrets.get("FIREBASE_API_KEY", ""),
            "authDomain": st.secrets.get("FIREBASE_AUTH_DOMAIN", ""),
            "projectId": st.secrets.get("FIREBASE_PROJECT_ID", ""),
            "storageBucket": st.secrets.get("FIREBASE_STORAGE_BUCKET", ""),
            "messagingSenderId": st.secrets.get("FIREBASE_MESSAGING_SENDER_ID", ""),
            "appId": st.secrets.get("FIREBASE_APP_ID", ""),
            "databaseURL": st.secrets.get("FIREBASE_DATABASE_URL", "")
        }

        # Validate configuration
        if not all(firebase_config.values()):
            st.error("Incomplete Firebase configuration. Please check your secrets.")
            return None, None

        # Initialize Firebase Admin SDK
        cred = credentials.Certificate(service_account_path)
        
        # Check if the app is already initialized
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred)

        # Initialize Pyrebase
        firebase = pyrebase.initialize_app(firebase_config)
        pyrebase_auth = firebase.auth()

        return firebase, pyrebase_auth

    except Exception as e:
        st.error(f"Firebase initialization error: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None, None

def signup_user(email, password, username):
    """
    Signup user with Firebase Authentication
    """
    try:
        # Create user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        
        return {
            "success": True,
            "user_id": user.uid,
            "email": user.email,
            "username": username
        }
    
    except auth.AuthError as e:
        error_code = e.code if hasattr(e, 'code') else 'unknown_error'
        error_message = str(e)
        
        error_map = {
            'EMAIL_EXISTS': "Email already in use",
            'INVALID_EMAIL': "Invalid email address",
            'WEAK_PASSWORD': "Password is too weak. Must be at least 6 characters."
        }
        
        return {
            "success": False,
            "error": error_map.get(error_code, f"Signup failed: {error_message}"),
            "code": error_code
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "code": "unexpected_error"
        }

def validate_email(email):
    """
    Validate email format
    """
    # Basic email validation regex
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email:
        return False, "Email cannot be empty"
    
    if not re.match(email_regex, email):
        return False, "Invalid email format"
    
    return True, ""

def login_user(email, password):
    """
    Login user with Firebase Authentication
    """
    # Validate email first
    email_valid, email_error = validate_email(email)
    if not email_valid:
        return {
            "success": False, 
            "error": email_error
        }

    try:
        # Use Pyrebase for login
        firebase, pyrebase_auth = initialize_firebase()
        if not firebase or not pyrebase_auth:
            return {"success": False, "error": "Firebase not initialized"}

        # Attempt to sign in
        user = pyrebase_auth.sign_in_with_email_and_password(email, password)
        
        return {
            "success": True,
            "user_id": user['localId'],
            "email": user['email'],
            "username": user.get('displayName', email.split('@')[0])
        }
    
    except Exception as e:
        # More detailed error logging
        import traceback
        print("Login Error Traceback:")
        traceback.print_exc()
        
        error_str = str(e)
        print(f"Raw Error String: {error_str}")
        
        # Comprehensive error mapping
        error_map = {
            "INVALID_LOGIN_CREDENTIALS": "Invalid email or password",
            "INVALID_PASSWORD": "Incorrect password",
            "INVALID_EMAIL": "Invalid email address",
            "USER_NOT_FOUND": "No account found with this email"
        }
        
        # Find the most specific error message
        for key, message in error_map.items():
            if key in error_str:
                return {"success": False, "error": message}
        
        # Fallback error message
        return {"success": False, "error": f"Login failed: {error_str}"}

def send_password_reset_email(email):
    """
    Send password reset email using Firebase Authentication
    """
    try:
        # Validate email first
        email_valid, email_error = validate_email(email)
        if not email_valid:
            return {"success": False, "error": email_error}
        
        # Initialize Firebase
        firebase = pyrebase.initialize_app({
            "apiKey": st.secrets["FIREBASE_API_KEY"],
            "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
            "projectId": st.secrets["FIREBASE_PROJECT_ID"],
            "databaseURL": st.secrets["FIREBASE_DATABASE_URL"],
            "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"]
        })
        
        try:
            # Send the reset email using Pyrebase
            auth = firebase.auth()
            auth.send_password_reset_email(email)
            
            return {
                "success": True, 
                "message": "Password reset link sent successfully! Please check your email."
            }
            
        except Exception as e:
            error_str = str(e)
            print(f"Firebase error details: {error_str}")  # For debugging
            
            # Map common Firebase error messages
            error_map = {
                "INVALID_EMAIL": "Invalid email address",
                "EMAIL_NOT_FOUND": "No account found with this email",
                "USER_NOT_FOUND": "No account found with this email",
                "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many reset attempts. Please try again later."
            }
            
            # Find the most specific error message
            for key, message in error_map.items():
                if key in error_str:
                    return {"success": False, "error": message}
            
            return {"success": False, "error": "Failed to send reset email. Please try again."}
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {"success": False, "error": "An unexpected error occurred. Please try again later."} 