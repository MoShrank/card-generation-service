import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from adapters import db_conn
from adapters.database_models.ModelConfig import (
    ModelConfig,
    QuestionAnswerGPTConfig,
)
from adapters.DBConnection import get_db_connection
from adapters.http_models.HttpModels import HTTPException
from adapters.repository import ConfigRepository
from adapters.vector_store.ChromaConnection import chroma_conn
from api import api_router
from config import env_config
from lib.GPT import (
    init_card_generation,
    init_qa_model,
    init_single_card_generator,
    init_summarizer,
)
from lib.util.limitier import limiter

uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.propagate = False
logging_format = "%(levelname)s - %(asctime)s - %(message)s"
logging.basicConfig(level=env_config.LOG_LEVEL, format=logging_format)
logger = logging.getLogger(__name__)


async def get_config(config_name: str) -> dict:
    db = get_db_connection()
    config_repo = ConfigRepository(db)
    config = await config_repo.find_one({"name": config_name})

    if not config:
        logger.error(f"Could not find model config for: {config_name}")
        raise Exception(f"Could not find model config for: {config_name}")

    return config


async def setup_prod_env() -> None:
    logger.info("Production environment detected")

    logger.info("Loading Card Generation model...")
    card_gen_cfg = ModelConfig(
        **(await get_config(env_config.CARD_GENERATION_CFG_NAME))
    )
    init_card_generation(card_gen_cfg)

    logger.info("Loading Summarizer model...")
    summarizer_cfg = ModelConfig(**(await get_config(env_config.SUMMARIZER_CFG_NAME)))
    init_summarizer(summarizer_cfg)

    logger.info("Loading Single Flashcard Generator Model")
    single_card_gen_cfg = ModelConfig(
        **(await get_config(env_config.SINGLE_CARD_GENERATION_CFG_NAME))
    )
    init_single_card_generator(single_card_gen_cfg)


async def setup_dev_env() -> None:
    logger.info("Development environment detected")
    init_card_generation()
    init_summarizer()
    init_single_card_generator()


env_setups = {"production": setup_prod_env, "development": setup_dev_env}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")

    logger.info("Connecting to MongoDB...")
    await db_conn.wait_for_connection()

    logger.info("Connecting to ChromaDB...")
    await chroma_conn.wait_for_connection()

    await env_setups[env_config.ENV]()

    logger.info("Loading Question Answer GPT model...")
    qagpt_model_config = QuestionAnswerGPTConfig(
        **(await get_config(env_config.QA_CFG_NAME))
    )
    init_qa_model(qagpt_model_config)

    yield


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(api_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(
    req: Request, exception: HTTPException
) -> JSONResponse:
    logger.error(f"{req.url.path} - Failed to process request. Error {exception.error}")
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "message": exception.message,
            "error": exception.error,
        },
    )


@app.get("/ping")
async def ping() -> dict:
    return {"ping": "pong!"}


if __name__ == "__main__":
    import uvicorn  # type: ignore

    uvicorn.run(app, host="0.0.0.0", port=8000)  # type: ignore
