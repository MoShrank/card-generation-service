from typing import Annotated

from fastapi import Depends

from adapters.DBConnection import DBConnection
from repository.BaseRepository import BaseRepository
from repository.DBConnection import get_db_connection

COLLECTION_NAME = "note"


class NoteRepository(BaseRepository):

    def __init__(self, db: Annotated[DBConnection, Depends(get_db_connection)]):
        super().__init__(COLLECTION_NAME, db)
