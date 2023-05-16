import time


def retry_on_exception(exception, max_retries=3, sleep_time=5):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exception:
                    retries += 1
                    if retries == max_retries:
                        raise
                time.sleep(sleep_time)

        return wrapper

    return decorator
