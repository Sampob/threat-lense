import sys

from app.config import Config
from app.models import db, Source, APIKey
from app.utils.logger import app_logger

from flask import Flask
from flask_migrate import Migrate
import redis

# Create a Redis connection
redis_client = redis.StrictRedis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=True
)

migrate = Migrate()

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
    
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Flask routes
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    with app.app_context():
        db.create_all()
        seed_sources()

    return app

def seed_sources():
    sources = [
        {"name": "AbuseIPDB", "requires_api_key": True},
        {"name": "Open Threat Exchange", "requires_api_key": True}
    ]
    
    for source_data in sources:
        existing_source = Source.query.filter_by(name=source_data['name']).first()

        if existing_source:
            print(f"Source '{source_data['name']}' already exists, skipping.")
            if existing_source.requires_api_key:
                api_key = APIKey.query.filter_by(source_name=source_data['name']).first()
                if api_key:
                    print(f"  -> API key is already configured for '{source_data['name']}'.")
                else:
                    print(f"  -> No API key configured for '{source_data['name']}'.")
        else:
            new_source = Source(
                name=source_data['name'],
                requires_api_key=source_data['requires_api_key']
            )
            db.session.add(new_source)
            print(f"Added new source '{source_data['name']}'.")

    db.session.commit()