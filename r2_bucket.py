import boto3
import json
from config import ACCESS_KEY, SECRET_KEY, API_BUCKET_NAME, R2_ENDPOINT_URL
from botocore.client import Config

# Initialize R2 Client
r2_client = boto3.client('s3',
                         region_name='auto',
                         endpoint_url=R2_ENDPOINT_URL,
                         aws_access_key_id=ACCESS_KEY,
                         aws_secret_access_key=SECRET_KEY,
                         config=Config(signature_version='s3v4'))

def save_api_key_data(api_key, data):
    json_data = json.dumps(data)
    file_name = f"api_keys/{api_key}.json"
    r2_client.put_object(Bucket=API_BUCKET_NAME, Key=file_name, Body=json_data)

def get_api_key_data(api_key):
    file_name = f"api_keys/{api_key}.json"
    try:
        response = r2_client.get_object(Bucket=API_BUCKET_NAME, Key=file_name)
        json_data = response['Body'].read().decode('utf-8')
        return json.loads(json_data)
    except r2_client.exceptions.NoSuchKey:
        return None
