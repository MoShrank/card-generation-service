import requests
from typing import Optional

MAX_RETRIES = 3


def get_content(url: str) -> Optional[str]:
    content = None

    for i in range(MAX_RETRIES):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                content = response.text
                break
        except Exception as e:
            print(f"Could not fetch page. Error: {e}")

    return content
