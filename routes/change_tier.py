from flask import Blueprint, request, jsonify
from config import TIER_INFO
from auth import authenticate
from r2_bucket import get_api_key_data, save_api_key_data

change_tier_bp = Blueprint('change_tier', __name__)

@change_tier_bp.route('/change_tier', methods=['POST'])
def change_tier():
    # Authentication to ensure that only authorized users can change tiers
    auth = request.authorization
    if not auth or not authenticate(auth.username, auth.password):
        return jsonify({"error": "Authentication Failed"}), 401

    # Check if request data is JSON
    if not request.is_json:
        return jsonify({"error": "Invalid JSON or Content-Type"}), 400

    data = request.get_json()
    api_key = data.get('api_key')
    new_tier = data.get('new_tier')

    # Validate new tier
    if new_tier not in TIER_INFO:
        return jsonify({"error": "Invalid tier"}), 400

    # Retrieve and update API key data
    api_key_data = get_api_key_data(api_key)
    if api_key_data is None:
        return jsonify({"error": "API key not found"}), 404

    api_key_data['tier'] = new_tier
    api_key_data['monthly_credits'] = TIER_INFO[new_tier]['monthly_credits']
    api_key_data['used_credits'] = 0
    api_key_data['call_count'] = 0

    # Save the updated data
    save_api_key_data(api_key, api_key_data)
    
    return jsonify({"message": f"API key tier changed to {new_tier}"}), 200
