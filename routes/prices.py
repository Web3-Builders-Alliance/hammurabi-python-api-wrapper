from flask import Blueprint, request, jsonify
from config import PRICE_BUCKET_NAME
from utilities.api_key_utils import check_api_key

prices_bp = Blueprint('prices_bp', __name__)

@prices_bp.route('/prices', methods=['GET'])
def price_files():
    api_key = request.headers.get('API-Key')
    error = check_api_key(api_key)
    if error:
        error_message, status_code = error
        return jsonify({"error": error_message}), status_code

    try:
        response = r2_client.list_objects_v2(Bucket=PRICE_BUCKET_NAME)
        file_list = [obj['Key'] for obj in response.get('Contents', [])]
        return jsonify({"files": file_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)})