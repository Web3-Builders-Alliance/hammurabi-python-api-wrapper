from flask import Blueprint, request, jsonify
from auth import authenticate
from r2_bucket import get_api_key_data, save_api_key_data
import logging 

whitelist_bp = Blueprint('admin_bp', __name__)

@whitelist_bp.route('/toggle_whitelist', methods=['POST'])
def toggle_whitelist(): 
    # Admin authentication 
    auth = request.authorization 
    if not auth or not authenticate(auth.username, auth.password): 
        return jsonify({"error": "Authentication failed"}), 401
    
    # Extract API Key 
    api_key = request.json.get('api_key')
    if not api_key: 
        return jsonify({"error": "API Key is required"}), 400
    
    # Retrieve existing API key data
    api_key_data = get_api_key_data(api_key)
    if api_key_data is None: 
        return jsonify({"error": "API key not found"}), 404
    
    # Toggle the whitelist status 
    api_key_data['whitelisted'] = not api_key_data.get('whitelisted', False)

    # Save the updated data
    save_api_key_data(api_key, api_key_data)

    return jsonify({"message": f"API key '{api_key}' whitelisting toggled", "whitelisted": api_key_data['whitelisted']}), 200