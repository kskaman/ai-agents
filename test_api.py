import os
import requests
import json
from dotenv import load_dotenv

# 1. load the vault
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

# Basic check so we don't crash with a confusing "NoneType" error if the key isn't set
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY is not set in the environment variables.")


# 2. Define the target
url = "https://api.anthropic.com/v1/messages"

# 3. Authenticate
headers = {
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

# 4. Construct the payload
payload = {
    "model": "claude-sonnet-4-6",
    "max_tokens": 4096,
    "messages": [
        {
            "role": "user",
            "content": "Hello, are you ready to code?"
        }
    ]
}

# 5. Fire! (No safety net)
print("Sending request to Anthropic API...")
response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)

# 6. Inspect the raw response
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    # Successful response, parse the JSON
    response_data = response.json()
    print("Response JSON:")
    print(json.dumps(response_data, indent=4))
else:
    # Error response, print the error message
    print("Error response:")
    try:
        error_data = response.json()
        print(json.dumps(error_data, indent=4))
    except json.JSONDecodeError:
        print(response.text)