from typing import Annotated

from fastapi import Depends

from adapters.DBConnection import DBConnection, get_db_connection
from adapters.repository.BaseRepository import BaseRepository

COLLECTION_NAME = "content"


class ContentRepository(BaseRepository):

    def __init__(self, db: Annotated[DBConnection, Depends(get_db_connection)]):
        super().__init__(COLLECTION_NAME, db)
