from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from api_statement_parser import parse_statement_from_file # Import the parsing function
import io

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

# API Routes
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/analyze-statement', methods=['POST'])
def analyze_statement():
    app.logger.info('Received analyze-statement request')
    # Check if a file is included in the request
    if 'file' not in request.files:
        app.logger.warning('No file part in request')
        return jsonify({'error': 'No file part in request'}), 400

    file = request.files['file']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        app.logger.warning('No selected file')
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            # Pass the file stream to the parsing function
            file_stream = io.BytesIO(file.read())
            file_stream.name = file.filename # Preserve the filename
            results = parse_statement_from_file(file_stream)
            app.logger.info('Successfully parsed statement')
            return jsonify(results), 200
        except Exception as e:
            app.logger.error(f'Error processing file: {e}')
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    app.logger.warning('Unexpected error processing file')
    return jsonify({'error': 'Unexpected error processing file'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000))) 