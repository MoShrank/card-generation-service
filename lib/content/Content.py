from typing import TypedDict

from adapters.database_models.Content import ContentSourceType


class Content(TypedDict):
    title: str
    source_type: ContentSourceType
    raw_text: str = None
    view_text: str = None
    source: str | bytes = None
