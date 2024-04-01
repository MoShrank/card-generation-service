import time
from typing import Any, Callable, Type


def retry_on_exception(
    exception: Type[Exception], max_retries: int = 3, sleep_time: int = 5
) -> Callable:
    def decorator(func: Callable):
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise Exception(
                            f"Failed to execute {func.__name__} after {max_retries} retries due to error: {e}"
                        ) from e
                time.sleep(sleep_time)

        return wrapper

    return decorator
