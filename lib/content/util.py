import base64
import io
import logging
from io import BytesIO
from typing import Optional
from urllib.parse import urlparse

import pypdf
import requests
from bs4 import BeautifulSoup  # type: ignore
from PIL import Image  # type: ignore

from config import env_config
from lib.util.error import retry_on_exception

logger = logging.getLogger(__name__)


headers = {
    "User-Agent": "Unknown User Agent",
}


@retry_on_exception(exception=Exception, max_retries=3)
def get_pdf_from_scihub(src: str) -> bytes:
    res = requests.post(env_config.SCIHUB_URL, data={"request": src}, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    iframe = soup.find("iframe", attrs={"id": "pdf"})
    src = iframe["src"]

    res = requests.get(src, headers=headers)

    return res.content


def get_title_from_pdf(pdf: bytes) -> Optional[str]:
    pdf_reader = pypdf.PdfReader(io.BytesIO(pdf))
    metadata = pdf_reader.metadata

    title = None

    if metadata and metadata.title:
        title = metadata.title

    return title


@retry_on_exception(exception=Exception, max_retries=3)
def scrape_url(url: str) -> str:
    response = requests.get(url, headers={**headers})

    if response.ok:
        return response.text
    else:
        raise Exception(f"Failed to get content from {url}. Response: {response}")


@retry_on_exception(exception=Exception, max_retries=3)
def get_readability(target_url: str, raw_content: str) -> dict:
    target_url = urlparse(target_url).netloc
    target_url = f"https://{target_url}"

    url = f"http://{env_config.READABILITY_SERVICE_HOST_NAME}/parse"
    data = {"url": target_url, "html": raw_content}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=data, headers=headers)

    if response.ok:
        return response.json()
    else:
        raise Exception(
            f"Failed to get readability doc from {url}. Response: {response}"
        )


def extract_content_from_url(url: str) -> dict:
    try:
        raw_content = scrape_url(url)
    except Exception as e:
        logger.error(f"Failed to extract info from webpage. Error: {e}")
        raise

    doc = get_readability(url, raw_content)

    title = doc["title"]
    view_text = doc["content"]
    image = get_image_from_html(view_text)

    if not image:
        image = get_image_from_html(raw_content)

    return {
        "title": title,
        "view_text": view_text,
        "raw_text": raw_content,
        "image": image,
    }


def get_image_from_html(readability: str) -> Optional[str]:
    soup = BeautifulSoup(readability, "html.parser")
    images = soup.find_all("img")

    if not images:
        return None

    resized_image_base64 = None

    for img in images:
        img_src = img.get("src")

        if "Schopenhauer" in img_src:
            print("foound", img_src)

        if not img_src:
            continue
        try:
            img_res = requests.get(img_src, headers=headers)
            resized_image = resize_image(img_res.content, 512, 512)
            resized_image_base64 = base64.b64encode(resized_image.getvalue()).decode(
                "utf-8"
            )
            break

        except Exception as e:
            if "Schopenhauer" in img_src:
                print("error in", img_src)
                logger.error(f"Failed to get image from {img_src}. Error: {e}")
            continue

    return resized_image_base64


def resize_image(image_content, max_width, max_height):
    """
    Resize an image to fit within the specified bounds of max_width and max_height,
    maintaining the aspect ratio.

    Parameters:
    - image_content: The binary content of the image.
    - max_width: The maximum width of the resized image.
    - max_height: The maximum height of the resized image.

    Returns:
    - A BytesIO object containing the resized image.
    """
    # Load the image from binary content
    image = Image.open(BytesIO(image_content))

    # Calculate the target size to maintain aspect ratio
    original_width, original_height = image.size
    ratio = min(max_width / original_width, max_height / original_height)
    new_size = (int(original_width * ratio), int(original_height * ratio))

    # Resize the image
    resized_image = image.resize(new_size, Image.Resampling.LANCZOS)

    # Save the resized image to a BytesIO object
    image_io = BytesIO()
    resized_image.save(image_io, format=image.format)
    image_io.seek(0)  # Move cursor to start of the file before reading

    return image_io
