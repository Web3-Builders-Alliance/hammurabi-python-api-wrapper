# File: routes/generate_key.py
from flask import request, jsonify
from config import BUCKET_NAME
from utilities.api_key_utils import check_api_key

@app.route('/raw_transactions', methods=['GET'])
def raw_transaction_files():
    api_key = request.headers.get('API-Key')
    error = check_api_key(api_key)
    if error:
        error_message, status_code = error
        return jsonify({"error": error_message}), status_code

    try:
        response = r2_client.list_objects_v2(Bucket=BUCKET_NAME)
        file_list = [obj['Key'] for obj in response.get('Contents', [])]
        return jsonify({"files": file_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)})