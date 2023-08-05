import requests

from util.error import retry_on_exception


@retry_on_exception(exception=Exception)
def get_content(url: str) -> str:
    content = None

    response = requests.get(url)

    if response.ok:
        content = response.text
    else:
        raise Exception(f"Failed to get content from {url}. Response: {response}")

    return content
