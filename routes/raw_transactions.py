from flask import Blueprint, request, jsonify
from config import BUCKET_NAME
from utilities.api_key_utils import check_api_key
from r2_bucket import r2_client_transaction
from botocore.exceptions import ClientError
import logging

raw_transactions_bp = Blueprint('raw_transactions_bp', __name__)

@raw_transactions_bp.route('/raw_transactions', methods=['GET'])
def raw_transaction_files():
    api_key = request.headers.get('API-Key')
    error = check_api_key(api_key)
    if error:
        error_message, status_code = error
        logging.error(f"API Key Check Failed: {error_message}")
        return jsonify({"error": error_message}), status_code

    try:
        response = r2_client_transaction.list_objects_v2(Bucket='orca-sol-usdc')
        all_objects = response.get('Contents', [])
        transaction_data = {}

        for obj in all_objects:
            object_content = r2_client_transaction.get_object(Bucket='orca-sol-usdc', Key=obj['Key'])
            content = object_content['Body'].read().decode('utf-8')
            transaction_data[obj['Key']] = content

        logging.info("All transaction data retrieved successfully.")
        return jsonify({"transactions": transaction_data}), 200

    except ClientError as e:
        logging.error(f"ClientError in retrieving objects: {e}")
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        logging.error(f"Unhandled Error: {str(e)}")
        return jsonify({"error": str(e)}), 500