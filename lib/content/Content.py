from typing import Optional, TypedDict

from adapters.database_models.Content import ContentSourceType


class ExtractedContent(TypedDict):
    title: str
    source_type: ContentSourceType
    raw_text: str = None
    view_text: str = None
    source: str = None
    pdf: Optional[bytes] = None
    image: Optional[str] = None
