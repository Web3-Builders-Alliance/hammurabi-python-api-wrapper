from flask import Blueprint, request, jsonify
from config import METADATA_BUCKET_NAME
from utilities.api_key_utils import check_api_key
from r2_bucket import r2_client_metadata
from botocore.exceptions import ClientError
import logging

metadata_bp = Blueprint('metadata_bp', __name__)

@metadata_bp.route('/metadata', methods=['GET'])
def metadata_files():
    api_key = request.headers.get('API-Key')
    error = check_api_key(api_key)
    if error:
        error_message, status_code = error
        logging.error(f"API Key Check Failed: {error_message}")
        return jsonify({"error": error_message}), status_code

    try:
        # List all objects in the bucket
        response = r2_client_metadata.get_object(Bucket='token-metadata', Key=f"token_metadata.json")
        all_keys = [obj['Key'] for obj in response.get('Contents', [])]
        logging.info(f"All keys in the bucket: {all_keys}")

        return jsonify({"keys": all_keys}), 200

    except ClientError as e:
        logging.error(f"ClientError in listing objects: {e}")
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        logging.error(f"Unhandled Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
