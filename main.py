import os
import boto3
import secrets
import datetime
import pytz
import json
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
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

# Initialize R2 Client
r2_client = boto3.client('s3',
                         region_name='auto',
                         endpoint_url=R2_ENDPOINT_URL,
                         aws_access_key_id=ACCESS_KEY,
                         aws_secret_access_key=SECRET_KEY,
                         config=Config(signature_version='s3v4'))

TIER_INFO = {
    "free": {"monthly_credits": 500000, "rate_limit": 200},
    "builder": {"monthly_credits": 2000000, "rate_limit": 200},
    "pro": {"monthly_credits": 5000000, "rate_limit": 500}
}

RATE_LIMIT_INTERVAL = datetime.timedelta(minutes=1)

def generate_api_key(tier="free"):
    return secrets.token_urlsafe(16)

def authenticate(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def save_api_key_data(api_key, data):
    json_data = json.dumps(data)
    file_name = f"api_keys/{api_key}.json"
    r2_client.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=json_data) # NEED TO SET UP NEW BUCKET HERE

def get_api_key_data(api_key):
    file_name = f"api_keys/{api_key}.json"
    try:
        response = r2_client.get_object(Bucket=BUCKET_NAME, Key=file_name)
        json_data = response['Body'].read().decode('utf-8')
        return json.loads(json_data)
    except r2_client.exceptions.NoSuchKey:
        return None

@app.route('/generate_api_key', methods=['POST'])
def generate_key():
    auth = request.authorization
    if not auth or not authenticate(auth.username, auth.password):
        return jsonify({"error": "Authentication Failed"}), 401

    new_key = generate_api_key()
    tier = request.args.get('tier', 'free')
    tier_info = TIER_INFO.get(tier, TIER_INFO["free"])

    api_key_data = {
        "tier": tier,
        "monthly_credits": tier_info["monthly_credits"],
        "used_credits": 0,
        "last_call": None,
        "call_count": 0,
        "whitelisted": False
    }
    save_api_key_data(new_key, api_key_data)
    return jsonify({"new_api_key": new_key, "tier": tier}), 200

@app.route('/change_tier', methods=['POST'])
def change_tier():
    # Authentication to ensure that only authorized users can change tiers
    auth = request.authorization
    if not auth or not authenticate(auth.username, auth.password):
        return jsonify({"error": "Authentication Failed"}), 401

    api_key = request.json.get('api_key')
    new_tier = request.json.get('new_tier')

    # Validate new tier
    if new_tier not in TIER_INFO:
        return jsonify({"error": "Invalid tier"}), 400

    # Retrieve and update API key data
    api_key_data = get_api_key_data(api_key)
    if api_key_data is None:
        return jsonify({"error": "API key not found"}), 404

    api_key_data['tier'] = new_tier
    api_key_data['monthly_credits'] = TIER_INFO[new_tier]['monthly_credits']
    # Resetting credits and call count might be necessary depending on your business logic
    api_key_data['used_credits'] = 0
    api_key_data['call_count'] = 0

    save_api_key_data(api_key, api_key_data)
    return jsonify({"message": f"API key tier changed to {new_tier}"}), 200

def check_api_key(api_key):
    key_info = get_api_key_data(api_key)
    if not key_info:
        return "Invalid or missing API Key", 401

    now = datetime.datetime.now(pytz.utc)

    if key_info["whitelisted"]:
        return None

    if key_info["last_call"] is None or key_info["last_call"].month != now.month:
        tier_info = TIER_INFO[key_info["tier"]]
        key_info["monthly_credits"] = tier_info["monthly_credits"]
        key_info["used_credits"] = 0

    rate_limit = TIER_INFO[key_info["tier"]]["rate_limit"]
    if key_info["last_call"] and now - key_info["last_call"] < RATE_LIMIT_INTERVAL:
        key_info["call_count"] += 1
        if key_info["call_count"] > rate_limit:
            return "Rate limit exceeded", 429
    else:
        key_info["call_count"] = 1

    key_info["last_call"] = now

    if key_info["used_credits"] >= key_info["monthly_credits"]:
        return "Monthly credit limit exceeded", 403

    key_info["used_credits"] += 1
    save_api_key_data(api_key, key_info)  

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
        return jsonify({"error": str(e)})

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
        return jsonify({"error": str(e)})

@app.route('/metadata', methods=['GET'])
def metadata_files():
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
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
