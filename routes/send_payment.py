from flask import Blueprint, request, jsonify
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.system_program import TransferParams, transfer
from solders.instruction import Instruction
from solders.message import MessageV0
from solders.hash import Hash
import json
from config import TIER_INFO
from r2_bucket import get_api_key_data, save_api_key_data
from datetime import datetime, timedelta

send_payment_bp = Blueprint('send_payment', __name__)

# Load the payment wallet information (The wallet receiving the USDC)
with open('./payment_wallet.json', 'r') as f:
    payment_wallet_data = json.load(f)
PAYMENT_WALLET = Keypair.from_bytes(payment_wallet_data)

# Load the payer wallet information (The wallet sending the USDC)
with open('./sender_wallet.json', 'r') as f: 
    user_wallet_data = json.load(f)
USER_WALLET = Keypair.from_bytes(user_wallet_data)

@send_payment_bp.route('/send_payment', methods=['POST'])
def create_payment_address():

    client = Client("https://api.devnet.solana.com")
    LAMPORT_PER_SOL = 1000000000

    data = request.get_json()
    user_wallet_address = USER_WALLET
    payment_wallet_address = PAYMENT_WALLET
    #airdrop = client.request_airdrop(USER_WALLET.pubkey(), 2 * LAMPORT_PER_SOL)
    token_amount = data.get('token_amount')
    api_key = data.get('api_key')  
    
    if token_amount == 0.05 or token_amount == 0.1:
        # Determine new tier and expiration date

            # Instructions 
        ix = transfer(
            TransferParams(
                from_pubkey = user_wallet_address.pubkey(), 
                to_pubkey = payment_wallet_address.pubkey(), 
                lamports = int(LAMPORT_PER_SOL*token_amount)
            )
        )

        blockhash_response = client.get_latest_blockhash()
        print(user_wallet_address.pubkey())
        
        # Send the transaction
        msg = MessageV0.try_compile(
            payer = user_wallet_address.pubkey(), 
            instructions = [ix], 
            address_lookup_table_accounts=[], 
            recent_blockhash = blockhash_response.value.blockhash,
        )

        tx = VersionedTransaction(msg, [user_wallet_address])

        client.send_transaction(tx)
        new_tier, expiration_date = determine_tier_and_expiration(token_amount)
        update_user_tier(api_key, new_tier, expiration_date)
        return jsonify({"payment_address": str(user_wallet_address.pubkey()), "amount_due": token_amount, "new_tier": new_tier}), 200
    else:
        return jsonify({"error": "Invalid payment amount."}), 400

def determine_tier_and_expiration(amount):
    expiration_date = datetime.now() + timedelta(days=30)
    if amount == 0.05:
        return 'builder', expiration_date
    elif amount == 0.1:
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

