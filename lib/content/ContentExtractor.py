import re
from typing import Annotated, Union

from fastapi import Depends

from adapters.database_models.Content import ContentSourceType
from adapters.SciPDFToMD import SciPDFToMD, SciPDFToMDInterface, get_pdf_to_markdown
from lib.content.Content import Content
from lib.content.util import (
    extract_content_from_url,
    get_pdf_from_scihub,
    get_title_from_pdf,
)

ContentT = Union[str, bytes]


class ContentExtractor:
    _pdf_to_markdown: SciPDFToMDInterface

    def __init__(
        self, pdf_to_markdown: Annotated[SciPDFToMD, Depends(get_pdf_to_markdown)]
    ):
        self._pdf_to_markdown = pdf_to_markdown

    def __call__(self, src: ContentT) -> Content:
        content_type = self.get_type_from_src(src)

        content = {}

        if content_type == "url":
            content = content | extract_content_from_url(src)
            content["source"] = src
        else:
            pdf = src

            if content_type == "doi":
                pdf = get_pdf_from_scihub(src)
                content["source"] = self._doi_input_to_url(src)

            markdown = self._pdf_to_markdown(pdf)

            content["title"] = get_title_from_pdf(pdf)
            content["raw_text"] = markdown
            content["view_text"] = markdown

        content["source_type"] = content_type

        return content

    def _doi_input_to_url(self, doi: str) -> str:
        if not doi.startswith("http"):
            doi = f"https://doi.org/{doi}"

        return doi

    def _is_doi(self, src: str) -> bool:
        doi_url_regex = r"^https?://(dx\.)?doi\.org/.*"

        return src.startswith("10.") or bool(re.match(doi_url_regex, src))

    def get_type_from_src(self, src: ContentT) -> ContentSourceType:
        if isinstance(src, bytes):
            return "pdf"
        elif self._is_doi(src):
            return "doi"
        else:
            return "url"
