from dataclasses import dataclass
from typing import Optional


@dataclass
class Content:
    title: str
    content: str
    raw_content: Optional[str]
