from dotenv import find_dotenv, load_dotenv
from pydantic import BaseSettings, Field


class EnvConfig(BaseSettings):
    OPENAI_API_KEY: str = Field(env="OPENAI_API_KEY")
    MONGO_DB_CONNECTION: str = Field(env="MONGO_DB_CONNECTION")
    USER_RATE_LIMIT_PER_MINUTE: str = Field(5, env="USER_RATE_LIMIT_PER_MINUTE")
    DECK_SERVICE_HOST_NAME: str = Field(
        "deck-management-service", env="DECK_MANAGEMENT_SERVICE_HOST_NAME"
    )
    DATABASE: str = Field("spacey", env="DATABASE")
    ENV: str = Field("development", env="ENV")
    MODEL_CONFIG_ID: str = Field(env="MODEL_CONFIG_ID")


load_dotenv(find_dotenv())
env_config = EnvConfig()
