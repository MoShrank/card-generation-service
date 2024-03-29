import io
import logging

import PyPDF2
import requests
from bs4 import BeautifulSoup  # type: ignore

from lib.content import Content
from lib.scraper import extract_info, extract_title
from util.error import retry_on_exception
from util.scraper import get_content

logger = logging.getLogger(__name__)


header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}
scihub_url = "https://sci-hub.hkvisa.net/"


@retry_on_exception(exception=Exception, max_retries=3)
def get_pdf_from_scihub(src: str) -> bytes:
    res = requests.post(scihub_url, data={"request": src}, headers=header)
    soup = BeautifulSoup(res.text, "html.parser")
    iframe = soup.find("iframe", attrs={"id": "pdf"})
    src = iframe["src"]

    res = requests.get(src, headers=header)

    return res.content


def get_info_from_pdf(pdf: bytes) -> Content:
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf))
    info = pdf_reader.metadata

    title = ""

    if info and info.title:
        title = info.title

    text = ""

    for page in pdf_reader.pages:
        text += page.extract_text()

    return Content(title=title, content=text, raw_content=text)


def get_text_from_paper_src(src: str) -> Content:
    try:
        pdf = get_pdf_from_scihub(src)
    except Exception as e:
        logger.error(f"Failed to get pdf from scihub: {e}")
        raise Exception from e
    try:
        info = get_info_from_pdf(pdf)
    except Exception as e:
        logger.error(f"Failed to extract info from pdf: {e}")
        raise Exception from e
    return info


def get_text_from_webpage(url: str) -> Content:
    try:
        raw_content = get_content(url)
    except Exception as e:
        logger.error(f"Failed to extract info from webpage. Error: {e}")
        raise Exception from e
    try:
        info = extract_info(raw_content)
    except Exception as e:
        logger.error(f"Failed to extract info from webpage. Error: {e}")
        raise Exception from e

    title = extract_title(raw_content) or info["title"]

    return Content(title=title, content=info["content"], raw_content=raw_content)
