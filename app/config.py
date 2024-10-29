import os

class Config:
    # Flask settings
    DEBUG = True
    FLASK_PORT = os.getenv("FLASK_PORT", 5000)
    LISTEN_TO_HOSTS = os.getenv("LISTEN_TO_HOSTS", "0.0.0.0")

    # Redis settings
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # Default to "redis" (Docker service name)
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    REDIS_DB = 0

    # Celery settings
    CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # Concurrency
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", 20))

    # Cache expiration settings
    CACHE_EXPIRATION = int(os.getenv("CACHE_EXPIRATION", 3600))  # Cache expiration in seconds (default 1 hour)

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///app_management.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "ET2Hri8wOF5dVplna91hLJfH2Ry3M1KMf1kCVddJrM0=")
    SQLALCHEMY_TRACK_MODIFICATIONS = False