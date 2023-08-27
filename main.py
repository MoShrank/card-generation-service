import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import dependencies
from config import env_config
from external.CardGeneration import CardGeneration, CardGenerationMock
from models.HttpModels import HTTPException
from models.ModelConfig import (
    CardGenerationConfig,
    QuestionAnswerGPTConfig,
    SummarizerConfig,
)
from models.PyObjectID import PyObjectID
from routes.notes import router as notes_router
from routes.web_content import router as web_content_router
from text.chroma_client import import_data, wait_for_chroma_connection
from text.QuestionAnswerGPT import QuestionAnswerGPT
from text.SingleFlashcardGenerator import (
    SingleFlashcardGenerator,
    SingleFlashcardGeneratorMock,
)
from text.Summarizer import Summarizer, SummarizerMock
from util.limitier import limiter

uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.propagate = False
logging_format = "%(levelname)s - %(asctime)s - %(message)s"
logging.basicConfig(level=env_config.LOG_LEVEL, format=logging_format)
logger = logging.getLogger(__name__)


async def get_config(id: str):
    object_id = PyObjectID(id)
    config = await dependencies.get_config_repo().find_one({"_id": object_id})

    if not config:
        logger.error(f"Could not find model config with id: {id}")
        raise Exception(f"Could not find model config with id: {id}")

    return config


async def setup_prod_env():
    logger.info("Production environment detected")

    logger.info("Loading Card Generation model...")
    model_config = await get_config(env_config.MODEL_CONFIG_ID)
    model_config = CardGenerationConfig(**model_config)
    dependencies.card_generation = CardGeneration(
        model_config, env_config.OPENAI_API_KEY
    )

    logger.info("Loading Summarizer model...")
    summarizer_model_config = await get_config(env_config.SUMMARIZER_CONFIG_ID)
    summarizer_model_config = SummarizerConfig(**summarizer_model_config)
    dependencies.summarizer = Summarizer(
        summarizer_model_config, env_config.OPENAI_API_KEY
    )

    logger.info("Loading Single Flashcard Generator Model")
    single_flashcard_model_config = await get_config(
        env_config.SINGLE_FLASHCARD_GENERATOR_CONFIG_ID
    )
    single_flashcard_model_config = CardGenerationConfig(
        **single_flashcard_model_config
    )
    dependencies.single_flashcard_generation = SingleFlashcardGenerator(
        single_flashcard_model_config, env_config.OPENAI_API_KEY
    )


async def setup_dev_env():
    logger.info("Development environment detected")
    dependencies.card_generation = CardGenerationMock()
    dependencies.summarizer = SummarizerMock()
    dependencies.single_flashcard_generation = SingleFlashcardGeneratorMock()


env_setups = {"production": setup_prod_env, "development": setup_dev_env}


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    logger.info("Starting up...")

    logger.info("Connecting to MongoDB...")
    await dependencies.db_conn.wait_for_connection()

    logger.info("Connecting to ChromaDB...")
    await wait_for_chroma_connection(5)

    logger.info("Importing data to ChromaDB...")
    await import_data()

    await env_setups[env_config.ENV]()

    logger.info("Loading Question Answer GPT model...")
    qagpt_model_config = await get_config(env_config.QAGPT_CONFIG_ID)
    qagpt_model_config = QuestionAnswerGPTConfig(**qagpt_model_config)
    dependencies.question_answer_gpt = QuestionAnswerGPT(
        qagpt_model_config, env_config.OPENAI_API_KEY
    )

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


if __name__ == "__main__":
    import uvicorn  # type: ignore

    uvicorn.run(app, host="0.0.0.0", port=8000)  # type: ignore
