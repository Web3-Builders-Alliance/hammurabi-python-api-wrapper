from flask import Flask, request, jsonify
import secrets
import boto3
import os
from botocore.client import Config 
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

# Cloudflare R2 Credentials and Bucket Name 
ACCESS_KEY = os.getenv('CLOUDFLARE_ACCESS_KEY')
SECRET_KEY = os.getenv('CLOUDFLARE_SECRET_KEY')
BUCKET_NAME = os.getenv('CLOUDFLARE_BUCKET_NAME')
R2_ENDPOINT_URL = os.getenv('CLOUDFLARE_API')

# Initialize R2 Client
r2_client = boto3.client('s3', 
                        region_name='auto',  # Dummy region
                        endpoint_url=R2_ENDPOINT_URL,
                        aws_access_key_id=ACCESS_KEY,
                        aws_secret_access_key=SECRET_KEY,
                        config=Config(signature_version='s3v4')) 

# API key storage, could be a database in production
api_keys = {
    "key1": {"credits": 100, "whitelisted": True},
    # Add more keys as needed
}

# Function to generate a new API key
def generate_api_key():
    return secrets.token_urlsafe(16)  # Generates a secure random URL-safe text string

@app.route('/generate_api_key', methods=['POST'])
def generate_key():
    # You should add authentication here to ensure only authorized users can access this endpoint

    new_key = generate_api_key()
    api_keys[new_key] = {"credits": 100, "whitelisted": False}  # New keys are not whitelisted by default

    return jsonify({"new_api_key": new_key}), 200

@app.route('/retrieve', methods=['GET'])
def retrieve_file():
    api_key = request.headers.get('API-Key')
    file_name = request.args.get('file_name') 

    if not api_key or api_key not in api_keys:
        return jsonify({"error": "Invalid or missing API Key"}), 401

    if not api_keys[api_key]['whitelisted'] and api_keys[api_key]['credits'] <= 0:
        return jsonify({"error": "No remaining credits"}), 403

    if not api_keys[api_key]['whitelisted']:
        api_keys[api_key]['credits'] -= 1

    try:
        file_object = r2_client.get_object(Bucket=BUCKET_NAME, Key=file_name)
        file_content = file_object['Body'].read().decode('utf-8')
        return jsonify({"file_content": file_content}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
