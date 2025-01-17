import sys

from app.config import Config
from app.models import db, Source, APIKey
from app.utils.cache import redis_client
from app.utils.source_registry import SourceRegistry
from app.utils.logger import app_logger

from flask import Flask
from flask_migrate import Migrate
from redis.exceptions import TimeoutError as RedisTimeoutError

migrate = Migrate()

# Flask app factory
def create_app(celery=False) -> Flask:
    if not celery:
        try:
            app_logger.debug(f"Testing connection to Redis at {Config.REDIS_HOST}:{Config.REDIS_PORT}")
            redis_client.ping()
            app_logger.debug("Connection successful, continuing initialization")
        except RedisTimeoutError as e:
            app_logger.error("Connection to Redis timed out, exiting")
            sys.exit()
    
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Flask routes
    if not celery:
        from app.routes import main as main_blueprint
        app.register_blueprint(main_blueprint)
        
        with app.app_context():
            db.create_all()
            seed_sources()

    return app

def seed_sources():
    source_instances = SourceRegistry.get_instance()
    sources = [{"name": cls.get_name(), "requires_api_key": cls.requires_api_key} for cls in source_instances.values()]
    all_configured_sources = Source.query.all()
    if all_configured_sources:
        app_logger.debug("Found existing db, checking for deprecated sources.")
        dict_of_names_of_new_sources = {d["name"] for d in sources}
        sources_not_in_new_sources: list[Source] = [src for src in all_configured_sources if src.name not in dict_of_names_of_new_sources]
        for s in sources_not_in_new_sources:
            remove_source = Source.query.filter_by(name=s.name).first()
            if remove_source:
                db.session.delete(remove_source)
                app_logger.warning(f"Removed deprecated source {remove_source.name}.")
        
    for source_data in sources:
        existing_source = Source.query.filter_by(name=source_data["name"]).first()
        if existing_source:
            app_logger.info(f"Source '{source_data['name']}' already exists, skipping creating db entry.")
            if existing_source.requires_api_key:
                api_key = APIKey.query.filter_by(source_name=source_data["name"]).first()
                if api_key:
                    app_logger.info(f"\t-> API key configured for '{source_data["name"]}'.")
                else:
                    app_logger.info(f"\t-> No API key configured for '{source_data["name"]}'.")
        else:
            new_source = Source(
                name=source_data["name"],
                requires_api_key=source_data["requires_api_key"]
            )
            db.session.add(new_source)
            app_logger.info(f"Added new source '{source_data["name"]}'.")

    db.session.commit()