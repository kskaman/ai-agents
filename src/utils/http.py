"""HTTP utility functions."""

import requests
import time


def request_with_retry(url, headers, payload, max_retries=10):
    """Make HTTP POST with retry on rate limit (429),
    server errors (5xx), and network failures"""

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, 
                                     json=payload, timeout=120)
        except requests.exceptions.RequestException as e:
            wait_time = 2 ** attempt
            print(f"Network error: {e}. Retrying in {wait_time}s ...")
            time.sleep(wait_time)
            continue

        if response.status_code == 429 or response.status_code >= 500:
            retry_after = response.headers.get("Retry-After")
            try:
                wait_time = int(retry_after) if retry_after else 2 ** attempt
            except (ValueError, TypeError):
                wait_time = 2 ** attempt

            
            print(f"Error {response.status_code}. Retrying in {wait_time}s ...")
            time.sleep(wait_time)
            continue

        if response.status_code >= 400:
            try:
                error_message = response.json()["error"]["message"]
            except (ValueError, KeyError):
                error_message = response.text
            raise Exception(f"API error {response.status_code}: {error_message}")

        return response

    raise Exception(f"Request failed after {max_retries} retries")
