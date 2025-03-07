import os
import json
import firebase_admin
from firebase_admin import credentials

def initialize_firebase_admin():
    """
    Initialize Firebase Admin SDK with robust error handling
    """
    # Possible paths for service account key
    possible_paths = [
        os.path.join(os.getcwd(), "firebase-service-account.json"),
        os.path.expanduser("~/firebase-service-account.json"),
        "./firebase-service-account.json"
    ]

    # Try to find and use the service account key
    for path in possible_paths:
        try:
            # Check if file exists
            if os.path.exists(path):
                # Validate file is a JSON
                with open(path, 'r') as f:
                    key_data = json.load(f)
                
                # Verify project ID
                if key_data.get('project_id') != 'loginform-jt':
                    print(f"Warning: Incorrect project ID in {path}")
                    continue

                # Initialize Firebase Admin SDK
                cred = credentials.Certificate(path)
                
                # Check if app is already initialized
                try:
                    firebase_admin.get_app()
                except ValueError:
                    # If not initialized, initialize the app
                    firebase_admin.initialize_app(cred)
                
                print(f"Firebase Admin SDK initialized successfully using {path}")
                return True

        except Exception as e:
            print(f"Error initializing Firebase Admin SDK with {path}: {e}")

    # If no valid service account key found
    print("Error: No valid Firebase service account key found.")
    print("Please download the service account key from Firebase Console.")
    return False

# Automatically initialize when module is imported
initialize_firebase_admin() 