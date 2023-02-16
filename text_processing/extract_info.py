from readability import Document
from bs4 import BeautifulSoup

remove_words = ["\n", "\r", "\\n", "\\r"]


def extract_info(content: str) -> dict:
    info = {}

    doc = Document(content)

    info["title"] = doc.title()

    content = doc.content()
    soup = BeautifulSoup(content)

    cleaned_text = soup.get_text()
    for word in remove_words:
        cleaned_text = cleaned_text.replace(word, "")

    info["content"] = cleaned_text

    return info
