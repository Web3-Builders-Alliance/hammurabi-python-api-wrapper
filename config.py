import os
from dotenv import load_dotenv

load_dotenv()

# Cloudflare R2 Credentials and Bucket Names
ACCESS_KEY = os.getenv('CLOUDFLARE_ACCESS_KEY')
SECRET_KEY = os.getenv('CLOUDFLARE_SECRET_KEY')
BUCKET_NAME = os.getenv('CLOUDFLARE_BUCKET_NAME')
PRICE_BUCKET_NAME = os.getenv('CLOUDFLARE_BUCKET_NAME_PRICE')
METADATA_BUCKET_NAME = os.getenv('CLOUDFLARE_BUCKET_NAME_METADATA')
R2_ENDPOINT_URL = os.getenv('CLOUDFLARE_API')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

TIER_INFO = {
    "free": {"monthly_credits": 500000, "rate_limit": 200},
    "builder": {"monthly_credits": 2000000, "rate_limit": 200},
    "pro": {"monthly_credits": 5000000, "rate_limit": 500}
}

RATE_LIMIT_INTERVAL = 60 
