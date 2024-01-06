from flask import Blueprint, request, jsonify
from config import TIER_INFO
from r2_bucket import save_api_key_data
from auth import authenticate
from datetime import datetime, timedelta
import secrets

def generate_api_key(tier="free"):
    return secrets.token_urlsafe(16)

generate_key_bp = Blueprint('generate_key_bp', __name__)

@generate_key_bp.route('/generate_api_key', methods=['POST'])
def generate_key():
    auth = request.authorization
    if not auth or not authenticate(auth.username, auth.password):
        return jsonify({"error": "Authentication Failed"}), 401

    new_key = generate_api_key()
    tier = request.args.get('tier', 'free')
    tier_info = TIER_INFO.get(tier, TIER_INFO["free"])

    far_future_date = datetime.now() + timedelta(days=3650)

    api_key_data = {
        "tier": tier,
        "monthly_credits": tier_info["monthly_credits"],
        "used_credits": 0,
        "last_call": None,
        "call_count": 0,
        "whitelisted": False, 
        "expiration_date": far_future_date.isoformat()
    }
    save_api_key_data(new_key, api_key_data)
    return jsonify({"new_api_key": new_key, "tier": tier}), 200