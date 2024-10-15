import os

class Config:
    # Flask settings
    DEBUG = True

    # Redis settings
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # Default to "redis" (Docker service name)
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    REDIS_DB = 0

    # Celery settings
    CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    # Cache expiration settings
    CACHE_EXPIRATION = 3600  # Cache expiration in seconds (1 hour)
