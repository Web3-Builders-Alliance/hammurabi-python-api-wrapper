from flask import Blueprint, request, jsonify
from config import METADATA_BUCKET_NAME
from utilities.api_key_utils import check_api_key
from r2_bucket import r2_client_metadata
import logging

prices_bp = Blueprint('prices_bp', __name__)

@prices_bp.route('/prices', methods=['GET'])
def price_files():
    api_key = request.headers.get('API-Key')
    error = check_api_key(api_key)
    if error:
        error_message, status_code = error
        logging.error(f"API Key Check Failed: {error_message}")
        return jsonify({"error": error_message}), status_code

    try:
        print(r2_client_metadata)
        response = r2_client_metadata.list_objects_v2(Bucket=METADATA_BUCKET_NAME, Prefix='token-price/')
        logging.info(f"R2 Bucket Response:{response}")
        file_list = []
        if 'Contents' in response:
            file_list = [obj['Key'] for obj in response['Contents'] if isinstance(obj['Key'], str)]
        logging.info(f"Metadata Files Retrieved: {file_list}")
        return jsonify({"files": file_list}), 200
    except Exception as e:
        logging.error(f"Error Retrieving Metadata: {str(e)}")
        return jsonify({"error": str(e)})