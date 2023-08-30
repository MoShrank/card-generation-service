from enum import Enum

from text.content.Content import Content
from text.content.util import (
    get_text_from_paper_src,
    get_text_from_webpage,
)


class ContentTypes(Enum):
    PAPER = "paper"
    WEBPAGE = "pdf"


class ContentExtractor:
    _type_extractor_map = {
        ContentTypes.PAPER: get_text_from_paper_src,
        ContentTypes.WEBPAGE: get_text_from_webpage,
    }

    def __call__(self, src: str) -> Content:
        content_type = self._get_type_from_src(src)
        content = self._type_extractor_map[content_type](src)

        return content

    def _get_type_from_src(self, src: str) -> ContentTypes:
        if src.startswith("http"):
            return ContentTypes.WEBPAGE
        else:
            return ContentTypes.PAPER
