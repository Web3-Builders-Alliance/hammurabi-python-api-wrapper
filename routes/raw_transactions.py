# File: routes/generate_key.py
from flask import Blueprint, request, jsonify
from config import BUCKET_NAME
from utilities.api_key_utils import check_api_key
from r2_bucket import r2_client_transaction

raw_transactions_bp = Blueprint('raw_transactions_bp', __name__)

@raw_transactions_bp.route('/raw_transactions', methods=['GET'])
def raw_transaction_files():
    api_key = request.headers.get('API-Key')
    error = check_api_key(api_key)
    if error:
        error_message, status_code = error
        return jsonify({"error": error_message}), status_code

    try:
        response = r2_client_transaction.list_objects_v2(Bucket='orca-sol-usdc')
        file_list = [obj['Key'] for obj in response.get('Contents', [])]
        return jsonify({"files": file_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)})