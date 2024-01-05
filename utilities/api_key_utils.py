import datetime
import pytz
from config import TIER_INFO, RATE_LIMIT_INTERVAL
from r2_bucket import get_api_key_data, save_api_key_data
import logging

def check_api_key(api_key):
    key_info = get_api_key_data(api_key)
    if not key_info:
        logging.error(f"API Key Not Found: {api_key}")
        return "Invalid or missing API Key", 401

    now = datetime.datetime.now(pytz.utc)

    # Check for subscription expiration
    expiration_date = datetime.datetime.fromisoformat(key_info["expiration_date"])
    if now > expiration_date:
        key_info['tier'] = 'free'  # Reset to free tier
        key_info['monthly_credits'] = TIER_INFO['free']['monthly_credits']
        key_info['used_credits'] = 0
        key_info['expiration_date'] = (now + datetime.timedelta(days=3650)).isoformat()  # Reset expiration date
        save_api_key_data(api_key, key_info)
        logging.info(f"API Key Tier Reset to Free: {api_key}")

    if key_info["whitelisted"]:
        logging.info(f"API Key Whitelisted: {api_key}")
        return None

    if isinstance(key_info["last_call"], str):
        key_info["last_call"] = datetime.datetime.fromisoformat(key_info["last_call"])

    if key_info["last_call"] is None or key_info["last_call"].month != now.month:
        tier_info = TIER_INFO[key_info["tier"]]
        key_info["monthly_credits"] = tier_info["monthly_credits"]
        key_info["used_credits"] = 0
        key_info["last_call"] = now.isoformat()
        save_api_key_data(api_key, key_info)
        logging.info(f"API Key Credits Reset: {api_key}")

    rate_limit = TIER_INFO[key_info["tier"]]["rate_limit"]
    if now - key_info["last_call"] < datetime.timedelta(seconds=RATE_LIMIT_INTERVAL):
        key_info["call_count"] += 1
        if key_info["call_count"] > rate_limit:
            logging.warning(f"Rate Limit Exceeded: {api_key}")
            return "Rate limit exceeded", 429
    else:
        key_info["call_count"] = 1
        key_info["last_call"] = now.isoformat()

    if key_info["used_credits"] >= key_info["monthly_credits"]:
        logging.warning(f"Credit Limit Exceeded: {api_key}")
        return "Monthly credit limit exceeded", 403

    key_info["used_credits"] += 1
    save_api_key_data(api_key, key_info)
    logging.info(f"API Key Checked: {api_key}")

    return None
