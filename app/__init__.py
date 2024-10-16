import sys

from app.config import Config
from app.utils.logger import app_logger

from flask import Flask
import redis

# Create a Redis connection
redis_client = redis.StrictRedis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=True
)

# Flask app factory
def create_app():
    try:
        app_logger.debug(f"Testing connection to Redis at {Config.REDIS_HOST}:{Config.REDIS_PORT}")
        redis_client.ping()
        app_logger.debug("Connection successful, continuing initialization")
    except redis.exceptions.TimeoutError as e:
        app_logger.error("Connection to Redis timed out, exiting")
        sys.exit()
    
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)

    # Register Flask routes
    from app.routes import configure_routes
    configure_routes(app)

    return app
