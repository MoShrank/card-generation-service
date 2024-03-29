from adapters.database_models.BaseMongoModel import BaseMongoModel


class User(BaseMongoModel):
    user_id: str
    total_no_generated: int
