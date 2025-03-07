import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog

def find_and_validate_service_account_key():
    """
    Find and validate Firebase service account key
    """
    # Open file dialog to select the key
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    file_path = filedialog.askopenfilename(
        title="Select Firebase Service Account Key",
        filetypes=[("JSON files", "*.json")]
    )
    
    if not file_path:
        print("No file selected.")
        return None
    
    try:
        with open(file_path, 'r') as f:
            key_data = json.load(f)
        
        # Validate key contents
        required_fields = [
            'type', 'project_id', 'private_key', 
            'client_email', 'client_id'
        ]
        
        missing_fields = [field for field in required_fields if field not in key_data]
        
        if missing_fields:
            print(f"Missing fields: {missing_fields}")
            return None
        
        if key_data.get('project_id') != 'loginform-jt':
            print("Incorrect project ID. Expected 'loginform-jt'")
            return None
        
        # Copy to project directory
        dest_path = os.path.join(os.getcwd(), "firebase-service-account.json")
        shutil.copy(file_path, dest_path)
        
        print(f"Successfully copied service account key to: {dest_path}")
        return dest_path
    
    except Exception as e:
        print(f"Error processing service account key: {e}")
        return None

def main():
    print("Firebase Service Account Key Helper")
    print("-----------------------------------")
    print("This tool will help you select and validate your Firebase service account key.")
    print("\nInstructions:")
    print("1. Click 'OK' to open file selection dialog")
    print("2. Navigate to and select your downloaded service account key JSON file")
    
    key_path = find_and_validate_service_account_key()
    
    if key_path:
        print("\n✅ Service Account Key Successfully Configured!")
        print(f"Location: {key_path}")
    else:
        print("\n❌ Failed to configure service account key.")
        print("Please ensure you've downloaded the key from Firebase Console.")

if __name__ == "__main__":
    main() 