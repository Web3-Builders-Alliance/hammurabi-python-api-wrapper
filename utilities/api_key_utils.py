# File: utilities/api_key_utils.py
import datetime
import pytz
from config import TIER_INFO, RATE_LIMIT_INTERVAL
from r2_bucket import get_api_key_data, save_api_key_data

def check_api_key(api_key):
    key_info = get_api_key_data(api_key)
    if not key_info:
        return "Invalid or missing API Key", 401

    now = datetime.datetime.now(pytz.utc)

    if key_info["whitelisted"]:
        return None

    if key_info["last_call"] is None or key_info["last_call"].month != now.month:
        tier_info = TIER_INFO[key_info["tier"]]
        key_info["monthly_credits"] = tier_info["monthly_credits"]
        key_info["used_credits"] = 0

    rate_limit = TIER_INFO[key_info["tier"]]["rate_limit"]
    if key_info["last_call"] and now - key_info["last_call"] < RATE_LIMIT_INTERVAL:
        key_info["call_count"] += 1
        if key_info["call_count"] > rate_limit:
            return "Rate limit exceeded", 429
    else:
        key_info["call_count"] = 1

    key_info["last_call"] = now

    if key_info["used_credits"] >= key_info["monthly_credits"]:
        return "Monthly credit limit exceeded", 403

    key_info["used_credits"] += 1
    save_api_key_data(api_key, key_info)  

    return None
