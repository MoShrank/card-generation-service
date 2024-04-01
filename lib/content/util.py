import io
import logging
from typing import Optional

import pypdf
import requests
from bs4 import BeautifulSoup  # type: ignore
from readability import Document  # type: ignore

from config import env_config
from lib.util.error import retry_on_exception

logger = logging.getLogger(__name__)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
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
    response = requests.get(url, headers=headers)

    if response.ok:
        return response.text
    else:
        raise Exception(f"Failed to get content from {url}. Response: {response}")


def extract_content_from_url(url: str) -> dict:
    try:
        raw_content = scrape_url(url)
    except Exception as e:
        logger.error(f"Failed to extract info from webpage. Error: {e}")
        raise

    doc = Document(raw_content)

    title = doc.title()
    view_text = doc.summary()

    return {"title": title, "view_text": view_text, "raw_text": raw_content}
