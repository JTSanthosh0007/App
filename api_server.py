from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from api_statement_parser import parse_statement_from_file # Import the parsing function
import io
import traceback

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
@app.route('/')
def index():
    return jsonify({
        'status': 'API is running',
        'endpoints': {
            'health': '/health',
            'analyze': '/analyze-statement'
        },
        'version': '1.0.0'
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/analyze-statement', methods=['POST'])
def analyze_statement():
    app.logger.info('Received analyze-statement request')
    try:
        # Check if a file is included in the request
        if 'file' not in request.files:
            app.logger.warning('No file part in request')
            return jsonify({'error': 'No file part in request'}), 400

        file = request.files['file']
        app.logger.info(f'Received file: {file.filename}')

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            app.logger.warning('No selected file')
            return jsonify({'error': 'No selected file'}), 400

        if not file.filename.lower().endswith('.pdf'):
            app.logger.warning(f'Invalid file type: {file.filename}')
            return jsonify({'error': 'Only PDF files are supported'}), 400

        # Pass the file stream to the parsing function
        file_stream = io.BytesIO(file.read())
        file_stream.name = file.filename  # Preserve the filename
        app.logger.info('Starting statement parsing')
        
        results = parse_statement_from_file(file_stream)
        app.logger.info('Successfully parsed statement')
        return jsonify(results), 200

    except Exception as e:
        app.logger.error(f'Error processing file: {str(e)}')
        app.logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Error processing file',
            'details': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested URL was not found on the server.',
        'available_endpoints': ['/', '/health', '/analyze-statement']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred.'
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.logger.info(f'Starting server on port {port}')
    app.run(host='0.0.0.0', port=port) 