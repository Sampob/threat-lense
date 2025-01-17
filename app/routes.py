from datetime import datetime, timezone
import json

from app.utils.indicator_type import is_valid_indicator
from app.utils.cache import cache_results, delete_from_cache, flush_cache
from app.utils.logger import setup_logger
from app.models import Source, APIKey, db

from flask import Blueprint, jsonify, request
from celery.result import AsyncResult

logger = setup_logger(__name__)

main = Blueprint("main", __name__)

@main.before_request
def log_request_info():
    logger.info(f"{request.method} request for {request.path}")

@main.errorhandler(400)
def bad_request_error(error):
    error_str = str(error)
    return jsonify({
        "error": "Bad Request",
        "message": error_str,
        "status_code": 400,
        "path": request.path,
        "timestamp": str(datetime.now(timezone.utc)),
    }), 400

@main.errorhandler(404)
def not_found_error(error):
    error_str = str(error)
    return jsonify({
        "error": "Not Found",
        "message": error_str,
        "status_code": 404,
        "path": request.path,
        "timestamp": str(datetime.now(timezone.utc)),
    }), 404

@main.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "successful", "message": "API is running"}), 200

@main.route("/purge", methods=["DELETE"])
def purge():
    flush_cache()
    return jsonify({"status": "successful", "message": "cache flushed successfully"}), 200

@main.route("/search", methods=["GET"])
def search():    
    from app.tasks import search_task
    indicator = request.json.get("indicator")
    if not indicator:
        return bad_request_error("Invalid parameter")
    
    logger.info(f"Received /search, with indicator: {indicator}")
    indicator = indicator.strip()
    if not is_valid_indicator(indicator):
        return bad_request_error(f"Invalid indicator: {indicator}")
    # Start Celery task
    task = search_task.delay(indicator)

    return jsonify({
        "status": "started",
        "task_id": task.id,
        "status_url": f"/search/status/{task.id}"
    }), 202

@main.route("/search/status/<task_id>", methods=["GET"])
def get_task_status(task_id):
    task_result = AsyncResult(task_id)
    
    if task_result.state == "PENDING":
        response = {
            "state": task_result.state,
            "status": "Pending..."
        }
    elif task_result.state == "FAILURE":
        response = {
            "state": task_result.state,
            "status": str(task_result.info),
        }
    elif task_result.state == "SUCCESS":
        response = {
            "state": task_result.state,
            "status": "Task completed successfully!"
        }
        if isinstance(task_result.result, str):
            response["result"] = json.loads(task_result.result)
        else:
            response["result"] = task_result.result
    else:
        response = {
            "state": task_result.state,
            "status": "Unknown state"
        }
    return jsonify(response), 200

@main.route("/sources", methods=["GET"])
def get_sources():    
    sources = Source.query.all()
        
    result = []
    for source in sources:
        result.append({
            "id": source.id,
            "name": source.name,
            "requires_api_key": source.requires_api_key,
            "api_key_configured": source.is_api_key_configured
        })
    
    return jsonify({"status": "successful", "sources": result}), 200

@main.route("/sources/configured", methods=["GET"])
def fetch_configured():
    all = APIKey.query.all()
    source_names = [i.source_name for i in all]
    return jsonify({"status": "successful", "configured_sources": source_names}), 200

@main.route("/sources/<source_id>", methods=["POST"])
def set_api_key(source_id):    
    api_key = request.json.get("api_key")
    if not api_key:
        return bad_request_error("Invalid parameter")
    
    source = Source.query.filter_by(name=source_id).first()
    if not source:
        source = Source.query.filter_by(id=source_id).first()
        if not source:
            return not_found_error("Source not found")

    if not source.requires_api_key:
        return bad_request_error("This source does not required an API key")
    
    api_key_entry = APIKey.query.filter_by(source_name=source.name).first()
    if not api_key_entry:
        api_key_entry = APIKey(source_name=source.name)

    # Set and save the encrypted API key
    api_key_entry.set_key(api_key)
    db.session.add(api_key_entry)
    db.session.commit()
    
    logger.debug("Change in API keys, flushing cached results")
    flush_cache()
    redis_key = f"api_key:{source.name}"
    cache_results(redis_key, api_key)

    return jsonify({"status": "successful", "message": f"API key for {source.name} set successfully"}), 200

@main.route("/sources/<source_id>", methods=["DELETE"])
def delete_api_key(source_id):    
    source = Source.query.filter_by(name=source_id).first()
    if not source:
        source = Source.query.filter_by(id=source_id).first()
        if not source:
            return not_found_error("Source not found")

    if not source.requires_api_key:
        return bad_request_error("This source does not required an API key")
    
    api_key_entry = APIKey.query.filter_by(source_name=source.name).first()
    
    if not api_key_entry:
        return not_found_error(f"No API key found for source {source.name}")
    
    logger.debug("Deleting API key from database")
    db.session.delete(api_key_entry)
    db.session.commit()
    
    logger.debug("Deleting API key from cache")
    redis_key = f"api_key:{source.name}"
    delete_from_cache(redis_key)
    
    return jsonify({"status": "successful", "message": f"API key for {source.name} deleted successfully"}), 200