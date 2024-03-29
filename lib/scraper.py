from typing import Optional

from bs4 import BeautifulSoup  # type: ignore
from readability import Document  # type: ignore

remove_words = ["\n", "\r", "\\n", "\\r"]
title_tags = ["h1", "h2", "h3"]


def extract_title(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, parser="lxml")

    title = None

    for tag in title_tags:
        title_tag = soup.find(tag)

        if title_tag:
            title = title_tag.text
            break

    return title


def extract_info(content: str) -> dict:
    info = {}

    doc = Document(content)

    info["title"] = doc.title()

    content = doc.content()
    soup = BeautifulSoup(content, parser="lxml")

    cleaned_text = soup.get_text()
    for word in remove_words:
        cleaned_text = cleaned_text.replace(word, "")

    info["content"] = cleaned_text

    return info
