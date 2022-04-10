import openai
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import env_config
from routes.notes import router
from util import limiter

openai.api_key = env_config.OPENAI_API_KEY

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(router)


@app.get("/ping")
async def ping():
    return {"ping": "pong!"}
