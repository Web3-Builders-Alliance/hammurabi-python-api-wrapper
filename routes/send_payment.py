from flask import Blueprint, request, jsonify
from config import TIER_INFO
from r2_bucket import get_api_key_data, save_api_key_data
import secrets
import requests
import json
from datetime import datetime, timedelta

send_payment_bp = Blueprint('send_payment', __name__)

PAYMENT_ADDRESS = "<PUBLIC_KEY>"

@send_payment_bp.route('/send_payment', methods=['POST'])
def create_payment_address():
    data = request.get_json()
    user_wallet_address = data.get('user_wallet_address')
    token_amount = data.get('token_amount')
    token_mint = data.get('token_mint')
    api_key = data.get('api_key')  # Assuming the API key is sent in the request
    transaction_id = data.get('transaction_id')  # Get the transaction ID from the request

    if len(user_wallet_address) != 44: 
        return jsonify({"error": "Invalid Solana public key. Please input a valid 44 character long key."}), 400
    
    if token_mint != 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v':  # USDC mint address on Solana
        return jsonify({"error": "Invalid token mint address. Please input the correct mint address for USDC"}), 400
    
    # Verify the transaction
    if not verify_transaction(transaction_id, user_wallet_address, token_amount):
        return jsonify({"error": "Transaction verification failed. Please ensure the transaction is completed."}), 400

    if token_amount == 15 or token_amount == 45:
        # Determine new tier and expiration date
        new_tier, expiration_date = determine_tier_and_expiration(token_amount)
        update_user_tier(api_key, new_tier, expiration_date)
        return jsonify({"payment_address": PAYMENT_ADDRESS, "amount_due": token_amount, "new_tier": new_tier}), 200
    else:
        return jsonify({"error": "Invalid payment amount."}), 400

def determine_tier_and_expiration(amount):
    expiration_date = datetime.now() + timedelta(days=30)
    if amount == 15:
        return 'builder', expiration_date
    elif amount == 45:
        return 'pro', expiration_date
    else:
        return 'free', expiration_date

def update_user_tier(api_key, new_tier, expiration_date):
    api_key_data = get_api_key_data(api_key)
    if api_key_data:
        api_key_data['tier'] = new_tier
        api_key_data['monthly_credits'] = TIER_INFO[new_tier]['monthly_credits']
        api_key_data['used_credits'] = 0
        api_key_data['call_count'] = 0
        api_key_data['expiration_date'] = expiration_date.isoformat() 
        save_api_key_data(api_key, api_key_data)

def verify_transaction(transaction_id, wallet_address, amount):
    rpc_url = "https://api.devnet.solana.com"

    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [transaction_id, "jsonParsed"]
    })

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(rpc_url, headers=headers, data=payload)
        response.raise_for_status()

        transaction_data = response.json()

        if 'error' in transaction_data: 
            print("Transaction error:", transaction_data['error'])
            return False 
        
        is_correct_sender = transaction_data['result']['meta']['postTokenBalances'][0]['owner'] == wallet_address
        is_correct_amount = transaction_data['result']['meta']['postTokenBalances'][0]['uiTokenAmount']['amount'] == str(amount)
        is_successful = transaction_data['result']['meta']['status']['Ok'] is not None

        return is_correct_sender and is_correct_amount and is_successful

    except requests.RequestException as e:
        print(f"Error querying the Solana RPC API: {e}")
        return False
