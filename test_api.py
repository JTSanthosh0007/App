import requests
import sys
import os

def test_health():
    response = requests.get('http://localhost:5000/health')
    print(f"Health check response: {response.status_code}")
    print(response.json())

def test_analyze_statement(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found")
        return

    with open(pdf_path, 'rb') as f:
        files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
        response = requests.post('http://localhost:5000/analyze-statement', files=files)
        
        print(f"Analysis response status: {response.status_code}")
        try:
            result = response.json()
            print("Response:", result)
        except Exception as e:
            print("Error parsing response:", e)
            print("Raw response:", response.text)

if __name__ == '__main__':
    test_health()
    if len(sys.argv) > 1:
        test_analyze_statement(sys.argv[1])
    else:
        print("Please provide a PDF file path as an argument") 