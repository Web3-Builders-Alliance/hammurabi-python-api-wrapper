from flask import request, jsonify
from config import TIER_INFO
from auth import authenticate
from r2_bucket import get_api_key_data

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