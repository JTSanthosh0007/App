import os
import streamlit as st

def debug_paths():
    print("Current Working Directory:", os.getcwd())
    print("Absolute path to service account:", os.path.abspath("firebase-service-account.json"))
    
    # Print out all secrets
    try:
        print("Available secrets:")
        for key in st.secrets.keys():
            print(f"{key}: {st.secrets[key]}")
    except Exception as e:
        print(f"Error accessing secrets: {e}")

if __name__ == "__main__":
    debug_paths() 