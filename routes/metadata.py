from flask import request, jsonify
from config import METADATA_BUCKET_NAME
from utilities.api_key_utils import check_api_key

@app.route('/metadata', methods=['GET'])
def metadata_files():
    api_key = request.headers.get('API-Key')
    error = check_api_key(api_key)
    if error:
        error_message, status_code = error
        return jsonify({"error": error_message}), status_code

    try:
        response = r2_client.list_objects_v2(Bucket=METADATA_BUCKET_NAME)
        file_list = [obj['Key'] for obj in response.get('Contents', [])]
        return jsonify({"files": file_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)})