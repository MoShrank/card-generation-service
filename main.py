import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import dependencies
from config import env_config
from models.HttpModels import HTTPException
from models.ModelConfig import (
    ModelConfig,
    QuestionAnswerGPTConfig,
    SummarizerConfig,
)
from routes.notes import router as notes_router
from routes.pdf import router as pdf_router
from routes.search import router as search_router
from routes.web_content import router as web_content_router
from text.chroma_client import import_data, wait_for_chroma_connection
from text.GPT.CardGeneration import CardGeneration, CardGenerationMock
from text.GPT.QuestionAnswerGPT import QuestionAnswerGPT
from text.GPT.SingleFlashcardGenerator import (
    SingleFlashcardGenerator,
    SingleFlashcardGeneratorMock,
)
from text.GPT.Summarizer import Summarizer, SummarizerMock
from text.SciPDFToMD import SciPDFToMD, SciPDFToMDMock
from util.limitier import limiter

uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.propagate = False
logging_format = "%(levelname)s - %(asctime)s - %(message)s"
logging.basicConfig(level=env_config.LOG_LEVEL, format=logging_format)
logger = logging.getLogger(__name__)


async def get_config(config_name: str):
    config = await dependencies.get_config_repo().find_one({"name": config_name})

    if not config:
        logger.error(f"Could not find model config for: {config_name}")
        raise Exception(f"Could not find model config for: {config_name}")

    return config


async def setup_prod_env():
    logger.info("Production environment detected")

    logger.info("Loading Card Generation model...")
    model_config = await get_config(env_config.CARD_GENERATION_CFG_NAME)
    model_config = ModelConfig(**model_config)
    dependencies.card_generation = CardGeneration(
        model_config, env_config.OPENAI_API_KEY
    )

    logger.info("Loading Summarizer model...")
    summarizer_model_config = await get_config(env_config.SUMMARIZER_CFG_NAME)
    summarizer_model_config = SummarizerConfig(**summarizer_model_config)
    dependencies.summarizer = Summarizer(
        summarizer_model_config, env_config.OPENAI_API_KEY
    )

    logger.info("Loading Single Flashcard Generator Model")
    single_flashcard_model_config = await get_config(
        env_config.SINGLE_CARD_GENERATION_CFG_NAME
    )
    single_flashcard_model_config = ModelConfig(**single_flashcard_model_config)
    dependencies.single_flashcard_generation = SingleFlashcardGenerator(
        single_flashcard_model_config, env_config.OPENAI_API_KEY
    )

    dependencies.pdf_to_md = SciPDFToMD()


async def setup_dev_env():
    logger.info("Development environment detected")
    dependencies.card_generation = CardGenerationMock()
    dependencies.summarizer = SummarizerMock()
    dependencies.single_flashcard_generation = SingleFlashcardGeneratorMock()
    dependencies.pdf_to_md = SciPDFToMDMock()


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
    qagpt_model_config = await get_config(env_config.QA_CFG_NAME)
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
app.include_router(pdf_router)
app.include_router(search_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(exception: HTTPException):
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
