import os
import boto3
import secrets
import datetime
import pytz
from dotenv import load_dotenv
from botocore.client import Config
from flask import Flask, request, jsonify

load_dotenv()
app = Flask(__name__)

# Cloudflare R2 Credentials and Bucket Names
ACCESS_KEY = os.getenv('CLOUDFLARE_ACCESS_KEY')
SECRET_KEY = os.getenv('CLOUDFLARE_SECRET_KEY')
BUCKET_NAME = os.getenv('CLOUDFLARE_BUCKET_NAME')
PRICE_BUCKET_NAME = os.getenv('CLOUDFLARE_BUCKET_NAME_PRICE')
METADATA_BUCKET_NAME = os.getenv('CLOUDFLARE_BUCKET_NAME_METADATA')
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
    "key1": {
        "tier": "free",
        "monthly_credits": 500000,
        "used_credits": 0,
        "last_call": None,
        "call_count": 0,
        "whitelisted": True
    },
    # Add more keys as needed
}

TIER_INFO = {
    "free": {"monthly_credits": 500000, "rate_limit": 200},
    "builder": {"monthly_credits": 2000000, "rate_limit": 200},
    "pro": {"monthly_credits": 5000000, "rate_limit": 500}
}

RATE_LIMIT_INTERVAL = datetime.timedelta(minutes=1)

def generate_api_key(tier="free"):
    return secrets.token_urlsafe(16)

@app.route('/generate_api_key', methods=['POST'])
def generate_key():
    # Add authentication and tier selection logic here for security

    new_key = generate_api_key()
    tier = request.args.get('tier', 'free')
    tier_info = TIER_INFO.get(tier, TIER_INFO["free"])

    api_keys[new_key] = {
        "tier": tier,
        "monthly_credits": tier_info["monthly_credits"],
        "used_credits": 0,
        "last_call": None,
        "call_count": 0,
        "whitelisted": False
    }
    return jsonify({"new_api_key": new_key, "tier": tier}), 200

def check_api_key(api_key):
    if not api_key or api_key not in api_keys:
        return "Invalid or missing API Key", 401

    now = datetime.datetime.now(pytz.utc)
    key_info = api_keys[api_key]

    # Skip checks for whitelisted keys
    if key_info["whitelisted"]:
        return None

    # Reset credits if a new month has started
    if key_info["last_call"] is None or key_info["last_call"].month != now.month:
        tier_info = TIER_INFO[key_info["tier"]]
        key_info["monthly_credits"] = tier_info["monthly_credits"]
        key_info["used_credits"] = 0

    # Check rate limit
    rate_limit = TIER_INFO[key_info["tier"]]["rate_limit"]
    if key_info["last_call"] and now - key_info["last_call"] < RATE_LIMIT_INTERVAL:
        key_info["call_count"] += 1
        if key_info["call_count"] > rate_limit:
            return "Rate limit exceeded", 429
    else:
        key_info["call_count"] = 1

    key_info["last_call"] = now

    # Deduct credit and check if limit exceeded
    if key_info["used_credits"] >= key_info["monthly_credits"]:
        return "Monthly credit limit exceeded", 403

    key_info["used_credits"] += 1

    return None

@app.route('/raw_transactions', methods=['GET'])
def raw_transaction_files():
    api_key = request.headers.get('API-Key')
    error = check_api_key(api_key)
    if error:
        error_message, status_code = error
        return jsonify({"error": error_message}), status_code

    try:
        response = r2_client.list_objects_v2(Bucket=BUCKET_NAME)
        file_list = [obj['Key'] for obj in response.get('Contents', [])]
        return jsonify({"files": file_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}
                       
@app.route('/prices', methods=['GET'])
def price_files():
    api_key = request.headers.get('API-Key')
    error = check_api_key(api_key)
    if error:
        error_message, status_code = error
        return jsonify({"error": error_message}), status_code

    try:
        response = r2_client.list_objects_v2(Bucket=PRICE_BUCKET_NAME)
        file_list = [obj['Key'] for obj in response.get('Contents', [])]
        return jsonify({"files": file_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}

@app.route('/metadata', methods=['GET'])
def price_files():
    api_key = request.headers.get('API-Key')
    error = check_api_key(api_key)
    if error:
        error_message, status_code = error
        return jsonify({"error": error_message}), status_code

    try:
        response = r2_client.list_objects_v2(Bucket=METADATA_BUCKET_NAME)
        file_list = [obj['Key'] for obj in response.get('Contents', [])]
        return jsonify({"files": file_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}