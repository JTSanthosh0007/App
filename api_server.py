from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime
import hashlib
import re
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')
handler = RotatingFileHandler('logs/api.log', maxBytes=10000, backupCount=1)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Initialize Firebase Admin
firebase_service_account_info = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT'))
cred = credentials.Certificate(firebase_service_account_info)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone):
    pattern = r'^\+?[1-9]\d{9,14}$'
    return bool(re.match(pattern, phone))

# API Routes
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/verify-email', methods=['POST'])
def verify_email():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
            
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
            
        hashed_password = hash_password(password)
            
        # Check if user exists
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1)
        results = query.get()
        
        if not results:
            return jsonify({"error": "User not found"}), 404
            
        user = results[0].to_dict()
        
        if user['password'] != hashed_password:
            return jsonify({"error": "Invalid password"}), 401
            
        return jsonify({
            "message": "Login successful",
            "user": {
                "email": user['email'],
                "username": user['username']
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error in verify_email: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/create-user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        phone = data.get('phone')
        
        if not all([email, username, password, phone]):
            return jsonify({"error": "All fields are required"}), 400
            
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
            
        if not validate_phone(phone):
            return jsonify({"error": "Invalid phone number format"}), 400
            
        # Check if email already exists
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1)
        results = query.get()
        
        if results:
            return jsonify({"error": "Email already registered"}), 409
            
        # Create new user
        hashed_password = hash_password(password)
        user_data = {
            'email': email,
            'username': username,
            'password': hashed_password,
            'phone': phone,
            'created_at': datetime.now().isoformat()
        }
        
        users_ref.add(user_data)
        
        return jsonify({
            "message": "User created successfully",
            "user": {
                "email": email,
                "username": username
            }
        }), 201
            
    except Exception as e:
        app.logger.error(f"Error in create_user: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000))) 