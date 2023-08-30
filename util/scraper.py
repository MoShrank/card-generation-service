import requests
from bs4 import BeautifulSoup  # type: ignore

from util.error import retry_on_exception

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@retry_on_exception(exception=Exception)
def get_content(url: str) -> str:
    content = None

    response = requests.get(url, headers=headers)

    if response.ok:
        content = response.text
    else:
        raise Exception(f"Failed to get content from {url}. Response: {response}")

    return content
