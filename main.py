import logging
from logging.config import dictConfig

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import dependencies
from config import env_config
from models.HttpModels import HTTPException
from models.ModelConfig import ModelConfig
from models.PyObjectID import PyObjectID
from routes.notes import router
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


app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exception: HTTPException):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "message": exception.message,
            "error": exception.error,
        },
    )


@app.on_event("startup")
async def startup_event():
    if env_config.ENV != "development":
        model_config_id = env_config.MODEL_CONFIG_ID
        model_config_id = PyObjectID(model_config_id)
        model_config = await dependencies.config_repo.find_one({"_id": model_config_id})
        model_config = ModelConfig(**model_config)

        dependencies.model_config = model_config
        dependencies.card_generation_api.set_config(model_config)


@app.get("/ping")
async def ping():
    return {"ping": "pong!"}
