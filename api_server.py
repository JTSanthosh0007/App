from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "message": "Service is running"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000) 