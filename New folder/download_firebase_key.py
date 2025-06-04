import os
import json
import shutil
import streamlit as st

def find_service_account_key():
    """
    Search for Firebase service account key in common locations
    """
    # Common download and project directories
    search_dirs = [
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Desktop"),
        os.getcwd(),
        os.path.dirname(os.path.abspath(__file__))
    ]

    # Possible filename patterns
    filename_patterns = [
        "*firebase*service*account*.json",
        "*loginform-jt*.json",
        "serviceAccountKey.json"
    ]

    import glob

    for search_dir in search_dirs:
        for pattern in filename_patterns:
            search_path = os.path.join(search_dir, pattern)
            matching_files = glob.glob(search_path)
            
            for file_path in matching_files:
                try:
                    with open(file_path, 'r') as f:
                        key_data = json.load(f)
                        
                    # Validate key contents
                    if (key_data.get('project_id') == 'loginform-jt' and 
                        'private_key' in key_data and 
                        'client_email' in key_data):
                        
                        # Destination path
                        dest_path = os.path.join(os.getcwd(), "firebase-service-account.json")
                        
                        # Copy the file
                        shutil.copy(file_path, dest_path)
                        return dest_path
                
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return None

def main():
    st.title("Firebase Service Account Key Setup")
    
    st.markdown("""
    ### Firebase Service Account Key Configuration
    
    #### Step-by-Step Guide:
    1. Go to Firebase Console
    2. Select "loginform-jt" project
    3. Project Settings (⚙️ icon)
    4. Service Accounts tab
    5. Click "Generate new private key"
    6. Save the downloaded JSON file
    """)
    
    # Attempt to find existing key
    found_key = find_service_account_key()
    
    if found_key:
        st.success(f"Firebase service account key found and configured at: {found_key}")
        st.balloons()
    else:
        st.error("Could not find a valid Firebase service account key.")
        st.warning("""
        ### Manual Setup Required
        
        1. Download the service account key from Firebase Console
        2. Rename the file to `firebase-service-account.json`
        3. Place it in the same directory as this script
        
        Recommended locations:
        - Current project directory
        - Downloads folder
        - Desktop
        """)

    # Additional debugging information
    st.markdown("### Debugging Information")
    st.write("Current Working Directory:", os.getcwd())
    st.write("Possible Search Directories:", [
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Desktop"),
        os.getcwd(),
        os.path.dirname(os.path.abspath(__file__))
    ])

if __name__ == "__main__":
    main() 