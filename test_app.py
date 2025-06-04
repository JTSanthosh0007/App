import requests
import os

def test_app():
    # Get the base URL from environment variable or use default
    base_url = os.getenv('NEXT_PUBLIC_API_URL', 'http://localhost:10000')
    
    try:
        # Test the health endpoint
        response = requests.get(f"{base_url}/health")
        print(f"Health check status: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing app: {str(e)}")
        return False

if __name__ == "__main__":
    test_app() 