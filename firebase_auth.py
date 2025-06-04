import requests
import streamlit as st
import hashlib
import json
import random
import string

def initialize_firebase():
    """
    Initialize Firebase configuration
    """
    # Get Firebase API key from secrets
    firebase_api_key = st.secrets.get("FIREBASE_API_KEY", "")
    if not firebase_api_key:
        print("Firebase API key not found in secrets")
        return None
    
    return {
        "api_key": firebase_api_key,
        "auth_domain": "statement-analyzer.firebaseapp.com",  # Update with your Firebase project
        "project_id": "statement-analyzer",  # Update with your Firebase project
    }

def firebase_signup(email, password, username, phone_number=None):
    """
    Create a new user with Firebase Authentication
    """
    firebase_config = initialize_firebase()
    if not firebase_config:
        return {"success": False, "error": "Firebase not configured"}
    
    try:
        # Firebase Auth REST API endpoint for signup
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={firebase_config['api_key']}"
        
        # Payload for creating user
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        # Make the request to Firebase
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            # User created successfully
            auth_data = response.json()
            
            # Now update the user profile with additional data
            update_url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={firebase_config['api_key']}"
            update_payload = {
                "idToken": auth_data["idToken"],
                "displayName": username,
                "photoUrl": "",  # Optional profile photo
                "returnSecureToken": True
            }
            
            update_response = requests.post(update_url, json=update_payload)
            
            if update_response.status_code == 200:
                # Store user data in session state
                st.session_state.user = {
                    "uid": auth_data["localId"],
                    "email": email,
                    "username": username,
                    "phone": phone_number,
                    "id_token": auth_data["idToken"],
                    "refresh_token": auth_data["refreshToken"]
                }
                
                return {
                    "success": True,
                    "user_id": auth_data["localId"],
                    "username": username,
                    "email": email
                }
            else:
                error_data = update_response.json()
                error_message = error_data.get("error", {}).get("message", "Failed to update user profile")
                return {"success": False, "error": error_message}
        else:
            # Handle signup errors
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            
            if error_message == "EMAIL_EXISTS":
                return {"success": False, "error": "Email already in use. Please use a different email or try logging in."}
            elif error_message == "WEAK_PASSWORD":
                return {"success": False, "error": "Password is too weak. Please use a stronger password."}
            else:
                return {"success": False, "error": f"Signup failed: {error_message}"}
    
    except Exception as e:
        print(f"Firebase signup error: {e}")
        return {"success": False, "error": str(e)}

def firebase_login(email, password):
    """
    Login with Firebase Authentication
    """
    firebase_config = initialize_firebase()
    if not firebase_config:
        return {"success": False, "error": "Firebase not configured"}
    
    try:
        # Firebase Auth REST API endpoint for login
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_config['api_key']}"
        
        # Payload for login
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        # Make the request to Firebase
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            # Login successful
            auth_data = response.json()
            
            # Get user profile data
            profile_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={firebase_config['api_key']}"
            profile_payload = {
                "idToken": auth_data["idToken"]
            }
            
            profile_response = requests.post(profile_url, json=profile_payload)
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                user_data = profile_data.get("users", [{}])[0]
                
                # Store user data in session state
                st.session_state.user = {
                    "uid": auth_data["localId"],
                    "email": email,
                    "username": user_data.get("displayName", "User"),
                    "id_token": auth_data["idToken"],
                    "refresh_token": auth_data["refreshToken"]
                }
                
                return {
                    "success": True,
                    "user_id": auth_data["localId"],
                    "username": user_data.get("displayName", "User"),
                    "email": email
                }
            else:
                # Still return success but with limited data
                st.session_state.user = {
                    "uid": auth_data["localId"],
                    "email": email,
                    "username": "User",
                    "id_token": auth_data["idToken"],
                    "refresh_token": auth_data["refreshToken"]
                }
                
                return {
                    "success": True,
                    "user_id": auth_data["localId"],
                    "username": "User",
                    "email": email
                }
        else:
            # Handle login errors
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            
            if error_message == "EMAIL_NOT_FOUND":
                return {"success": False, "error": "Email not found. Please check your email or sign up."}
            elif error_message == "INVALID_PASSWORD":
                return {"success": False, "error": "Invalid password. Please try again."}
            elif error_message == "USER_DISABLED":
                return {"success": False, "error": "This account has been disabled."}
            else:
                return {"success": False, "error": f"Login failed: {error_message}"}
    
    except Exception as e:
        print(f"Firebase login error: {e}")
        return {"success": False, "error": str(e)}

def firebase_send_password_reset(email):
    """
    Send password reset email using Firebase
    """
    firebase_config = initialize_firebase()
    if not firebase_config:
        return {"success": False, "error": "Firebase not configured"}
    
    try:
        # Firebase Auth REST API endpoint for password reset
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={firebase_config['api_key']}"
        
        # Payload for password reset
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }
        
        # Make the request to Firebase
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Password reset instructions sent to your email"
            }
        else:
            # Handle errors
            error_data = response.json()
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            
            if error_message == "EMAIL_NOT_FOUND":
                return {"success": False, "error": "Email not found. Please check your email or sign up."}
            else:
                return {"success": False, "error": f"Password reset failed: {error_message}"}
    
    except Exception as e:
        print(f"Firebase password reset error: {e}")
        return {"success": False, "error": str(e)}

def firebase_logout():
    """
    Logout the current user
    """
    if "user" in st.session_state:
        del st.session_state.user
    
    return {"success": True}

def firebase_google_auth_url():
    """
    Generate the Google authentication URL for Firebase
    """
    firebase_config = initialize_firebase()
    if not firebase_config:
        print("Firebase configuration not found")
        return None
    
    # Check if Google Client ID is available
    google_client_id = st.secrets.get('GOOGLE_CLIENT_ID', '')
    if not google_client_id:
        print("Google Client ID not found in secrets")
        return None
    
    print(f"Firebase config: {firebase_config}")
    print(f"Google Client ID available: {bool(google_client_id)}")
    
    # Generate a random state parameter for security
    state = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    st.session_state.oauth_state = state
    
    # Store the current page to redirect back after auth
    st.session_state.pre_auth_page = st.session_state.get('current_page', 'login')
    
    # Build the OAuth URL
    api_key = firebase_config["api_key"]
    redirect_uri = "https://statement-analyzer.streamlit.app/callback"  # Update with your app URL
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={google_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=email%20profile&"
        f"state={state}&"
        f"prompt=select_account"
    )
    
    print(f"Generated auth URL: {auth_url[:50]}...")
    return auth_url

def handle_google_callback(code, state):
    """
    Handle the callback from Google OAuth
    """
    # Verify state parameter to prevent CSRF attacks
    if state != st.session_state.get('oauth_state'):
        return {"success": False, "error": "Invalid state parameter"}
    
    firebase_config = initialize_firebase()
    if not firebase_config:
        return {"success": False, "error": "Firebase not configured"}
    
    try:
        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        redirect_uri = "https://statement-analyzer.streamlit.app/callback"  # Update with your app URL
        
        token_payload = {
            "code": code,
            "client_id": st.secrets.get('GOOGLE_CLIENT_ID', ''),
            "client_secret": st.secrets.get('GOOGLE_CLIENT_SECRET', ''),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        token_response = requests.post(token_url, data=token_payload)
        
        if token_response.status_code != 200:
            return {"success": False, "error": "Failed to exchange code for tokens"}
        
        token_data = token_response.json()
        id_token = token_data.get("id_token")
        
        # Sign in to Firebase with Google credential
        firebase_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={firebase_config['api_key']}"
        firebase_payload = {
            "postBody": f"id_token={id_token}&providerId=google.com",
            "requestUri": "https://statement-analyzer.streamlit.app",
            "returnIdpCredential": True,
            "returnSecureToken": True
        }
        
        firebase_response = requests.post(firebase_url, json=firebase_payload)
        
        if firebase_response.status_code != 200:
            return {"success": False, "error": "Failed to sign in with Google"}
        
        # Process Firebase response
        firebase_data = firebase_response.json()
        
        # Store user data in session state
        st.session_state.user = {
            "uid": firebase_data["localId"],
            "email": firebase_data["email"],
            "username": firebase_data.get("displayName", "User"),
            "id_token": firebase_data["idToken"],
            "refresh_token": firebase_data["refreshToken"],
            "provider": "google.com"
        }
        
        return {
            "success": True,
            "user_id": firebase_data["localId"],
            "username": firebase_data.get("displayName", "User"),
            "email": firebase_data["email"]
        }
        
    except Exception as e:
        print(f"Google auth error: {e}")
        return {"success": False, "error": str(e)} 