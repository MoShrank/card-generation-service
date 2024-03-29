from dataclasses import dataclass


@dataclass
class Content:
    title: str
    content: str
    raw_content: str
