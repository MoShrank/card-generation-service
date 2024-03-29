from datetime import datetime
from typing import Optional

from adapters.database_models.BaseMongoModel import BaseMongoModel


class WebContent(BaseMongoModel):
    name: str
    user_id: str
    url: str
    title: str
    content: str
    html: str
    summary: str
    deleted_at: Optional[datetime]
