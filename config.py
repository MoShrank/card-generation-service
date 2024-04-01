from typing import Literal

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseSettings, Field, validator


class EnvConfig(BaseSettings):
    PORT: int = Field(8000, env="PORT")
    LOG_LEVEL: str = Field("info", env="LOG_LEVEL")
    OPENAI_API_KEY: str = Field(None, env="OPENAI_API_KEY")
    MONGO_DB_CONNECTION: str = Field(
        "mongodb://127.0.0.1:27017", env="MONGO_DB_CONNECTION"
    )
    USER_RATE_LIMIT_PER_MINUTE: str = Field(5, env="USER_RATE_LIMIT_PER_MINUTE")
    DECK_SERVICE_HOST_NAME: str = Field(
        "deck-management-service", env="DECK_MANAGEMENT_SERVICE_HOST_NAME"
    )
    DATABASE: str = Field("spacey", env="DATABASE")
    ENV: Literal["development", "production"] = Field("development", env="ENV")
    MAX_TEXT_LENGTH: int = Field(1000, env="MAX_TEXT_LENGTH")
    CHROMA_HOST: str = Field("localhost", env="CHROMA_HOST")
    CHROMA_PORT: str = Field("8000", env="CHROMA_PORT")

    BERT_MODEL_PATH: str = Field(
        "distilbert/distilbert-base-cased-distilled-squad", env="BERT_MODEL_PATH"
    )

    QA_CFG_NAME: str = Field("qa", env="QA_CFG_NAME")
    CARD_GENERATION_CFG_NAME: str = Field(
        "card_generation", env="CARD_GENERATION_CFG_NAME"
    )
    SUMMARIZER_CFG_NAME: str = Field("summarization", env="SUMMARIZER_CFG_NAME")
    SINGLE_CARD_GENERATION_CFG_NAME: str = Field(
        "single_card_generation", env="SINGLE_CARD_GENERATION_CFG_NAME"
    )

    AWS_SECRET_KEY: str = Field(None, env="AWS_SECRET_KEY")
    AWS_ACCESS_KEY: str = Field(None, env="AWS_ACCESS_KEY")

    SCIHUB_URL: str = Field("https://sci-hub.hkvisa.net/", env="SCIHUB_URL")

    @validator("LOG_LEVEL", pre=True)
    def transform_log_level(cls, log_level):
        return log_level.upper()

    def is_dev(self):
        return self.ENV == "development"

    def is_prod(self):
        return self.ENV == "production"


load_dotenv(find_dotenv())
env_config = EnvConfig()  # type: ignore
