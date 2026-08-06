import time
from functools import wraps


def retry(max_attempts=3, delay=1):
    """
    Simple retry decorator.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            last_exception = None

            for attempt in range(max_attempts):

                try:
                    return func(*args, **kwargs)

                except Exception as exc:

                    last_exception = exc

                    if attempt < max_attempts - 1:
                        time.sleep(delay)

            raise last_exception

        return wrapper

    return decorator