import re
import json
import os

def parse_headers(headers_text):
    """
    Universal parser that handles:
    1. Firefox: Copy Request Headers (Key: Value on lines)
    2. Chrome: Copy as cURL (bash) with -H 'key: value'
    """
    headers = {}
    text = headers_text.strip()
    
    # METHOD 1: cURL bash format (-H 'name: value')
    curl_h_pattern = r"-H\s+'([^']+):\s*([^']+)'"
    for key, value in re.findall(curl_h_pattern, text):
        headers[key.strip().lower()] = value.strip()
    
    # METHOD 1b: cURL cookie (-b 'cookie')
    curl_cookie_pattern = r"-b\s+'([^']+)'"
    cookie_match = re.search(curl_cookie_pattern, text)
    if cookie_match:
        headers['cookie'] = cookie_match.group(1).strip()
    
    # METHOD 2: Raw format like Firefox (Name: Value on lines)
    # Only do this if cURL didn't work or we're missing critical headers
    if not headers or 'x-goog-visitor-id' not in headers:
        lines = text.split('\n')
        for line in lines:
            if ':' in line and not line.startswith('curl'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    # Only capture if not already found or value is longer
                    if key not in headers or len(value) > len(headers.get(key, '')):
                        headers[key] = value
    
    return headers

def validate_headers(headers):
    """
    Check if all required headers are present.
    Returns (is_valid, missing_keys_list)
    """
    required = ['cookie', 'authorization', 'x-goog-authuser', 'x-goog-visitor-id']
    missing = [key for key in required if key not in headers]
    return (len(missing) == 0, missing)

def save_browser_auth(headers, file_path='browser_auth.json'):
    """
    Save headers to browser_auth.json with the correct structure.
    """
    auth_data = {
        "accept": headers.get("accept", "*/*"),
        "accept-language": headers.get("accept-language", "en-US,en;q=0.9"),
        "content-type": headers.get("content-type", "application/json"),
        "cookie": headers["cookie"],
        "user-agent": headers.get("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
        "x-goog-authuser": headers.get("x-goog-authuser", "0"),
        "x-goog-visitor-id": headers["x-goog-visitor-id"],
        "authorization": headers["authorization"],
        "origin": headers.get("origin", "https://music.youtube.com")
    }
    
    with open(file_path, "w") as f:
        json.dump(auth_data, f, indent=2)
    
    return True
