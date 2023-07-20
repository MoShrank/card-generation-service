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
    ENV: str = Field("development", env="ENV")
    MODEL_CONFIG_ID: str = Field(None, env="MODEL_CONFIG_ID")
    SUMMARIZER_CONFIG_ID: str = Field(None, env="SUMMARIZER_CONFIG_ID")
    MAX_TEXT_LENGTH: int = Field(1000, env="MAX_TEXT_LENGTH")
    CHROMA_HOST: str = Field("localhost", env="CHROMA_HOST")
    CHROMA_PORT: str = Field("8000", env="CHROMA_PORT")
    QAGPT_CONFIG_ID: str = Field(None, env="QAGPT_CONFIG_ID")

    @validator("LOG_LEVEL", pre=True)
    def transform_log_level(cls, log_level):
        return log_level.upper()


load_dotenv(find_dotenv())
env_config = EnvConfig()  # type: ignore
