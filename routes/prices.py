from flask import Blueprint, request, jsonify
from config import PRICE_BUCKET_NAME
from utilities.api_key_utils import check_api_key
from r2_bucket import r2_client_metadata
from botocore.exceptions import ClientError
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
        response = r2_client_metadata.list_objects_v2(Bucket='token-price')
        all_objects = response.get('Contents', [])
        prices_data = {}

        for obj in all_objects:
            object_content = r2_client_metadata.get_object(Bucket='token-price', Key=obj['Key'])
            content = object_content['Body'].read().decode('utf-8')
            prices_data[obj['Key']] = content

        logging.info("All prices data retrieved successfully.")
        return jsonify({"prices": prices_data}), 200

    except ClientError as e:
        logging.error(f"ClientError in retrieving objects: {e}")
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        logging.error(f"Unhandled Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
