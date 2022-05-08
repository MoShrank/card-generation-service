from fastapi import Request
from slowapi import Limiter


def get_user_id(request: Request):
    user_id = request.query_params.get("user_id")
    return user_id


limiter = Limiter(key_func=get_user_id)
