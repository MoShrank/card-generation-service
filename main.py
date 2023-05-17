import logging
from contextlib import asynccontextmanager
from logging.config import dictConfig

import nltk
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import dependencies
from config import env_config
from external.CardGeneration import (
    CardGeneration,
    CardGenerationMock,
)
from models.HttpModels import HTTPException
from models.ModelConfig import CardGenerationConfig, SummarizerConfig
from models.PyObjectID import PyObjectID
from routes.notes import router as notes_router
from routes.web_content import router as web_content_router
from text.Summarizer import Summarizer, SummarizerMock
from util.limitier import limiter


class LogConfig(BaseModel):
    LOGGER_NAME: str = "logger"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        "logger": {"handlers": ["default"], "level": LOG_LEVEL},
    }


dictConfig(LogConfig().dict())


async def get_config(id: str):
    object_id = PyObjectID(id)
    config = await dependencies.config_repo.find_one({"_id": object_id})

    if not config:
        logging.error(f"Could not find model config with id: {id}")
        raise Exception(f"Could not find model config with id: {id}")

    return config


@asynccontextmanager
async def lifespan(app: FastAPI):
    nltk.download("punkt")
    logging.info("Starting up...")
    if env_config.ENV == "production":
        logging.info("Production environment detected")

        logging.info("Loading Card Generation model...")
        model_config = await get_config(env_config.MODEL_CONFIG_ID)
        model_config = CardGenerationConfig(**model_config)
        dependencies.card_generation = CardGeneration(
            model_config, env_config.OPENAI_API_KEY
        )

        logging.info("Loading Summarizer model...")
        summarizer_model_config = await get_config(env_config.SUMMARIZER_CONFIG_ID)
        summarizer_model_config = SummarizerConfig(**summarizer_model_config)
        dependencies.summarizer = Summarizer(
            summarizer_model_config, env_config.OPENAI_API_KEY
        )

    else:
        dependencies.card_generation = CardGenerationMock()
        dependencies.summarizer = SummarizerMock()

    yield


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(notes_router)
app.include_router(web_content_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exception: HTTPException):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "message": exception.message,
            "error": exception.error,
        },
    )


@app.get("/ping")
async def ping():
    return {"ping": "pong!"}
