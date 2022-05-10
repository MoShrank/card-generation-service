from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import dependencies
from config import env_config
from models.ModelConfig import ModelConfig
from models.PyObjectID import PyObjectID
from routes.notes import router
from util.limitier import limiter

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(router)


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
