import time
import random
import logging

logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries=5, initial_delay=2.0, backoff_factor=2.0, jitter=True):
    """
    Decorator to retry a function call with exponential backoff and jitter.
    Specifically targets transient exceptions (429 Rate Limits, 503 High Demand, timeouts).
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    msg = str(e).lower()
                    
                    # Detect common transient failures
                    is_retryable = (
                        "429" in msg or 
                        "503" in msg or 
                        "resource_exhausted" in msg or 
                        "unavailable" in msg or
                        "timeout" in msg or
                        "deadline_exceeded" in msg or
                        isinstance(e, (ConnectionError, TimeoutError))
                    )
                    
                    # If it's not retryable or we are out of retries, raise the exception
                    if not is_retryable or attempt == max_retries - 1:
                        logger.error(f"Function {func.__name__} failed permanently on attempt {attempt + 1}: {e}")
                        raise e
                    
                    # Calculate wait time with optional jitter
                    sleep_time = delay
                    if jitter:
                        sleep_time += random.uniform(0, 1.0)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for '{func.__name__}' with error: '{e}'. "
                        f"Retrying in {sleep_time:.2f} seconds..."
                    )
                    
                    time.sleep(sleep_time)
                    delay *= backoff_factor
            return func(*args, **kwargs)
        return wrapper
    return decorator
