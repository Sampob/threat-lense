from datetime import datetime, timezone
import json

from app.tasks import search_task
from app.utils.indicator_type import is_valid_indicator
from app.utils.cache import fetch_from_cache
from app.utils.logger import setup_logger
from app.models import Source, APIKey, db

from flask import Blueprint, jsonify, request

logger = setup_logger(__name__)

main = Blueprint("main", __name__)

@main.errorhandler(400)
def bad_request_error(error):
    return jsonify({
        "error": "Bad Request",
        "message": f"The request could not be processed: {error}",
        "status_code": 400,
        "path": request.path,
        "timestamp": str(datetime.now(timezone.utc)),
        "hint": "Ensure all required parameters are provided and valid."
    }), 400

@main.route("/search", methods=["GET"])
def search():
    indicator = request.json.get("indicator")
    
    logger.info(f"Flask request for /search, with indicator: {indicator}")
    if not is_valid_indicator(indicator):
        return bad_request_error(f"Invalid indicator {indicator}")
    # Start Celery task
    task = search_task.delay(indicator)

    return jsonify({
        "task_id": task.id,
        "status_url": f"/search/status/{task.id}"
    }), 202

@main.route("/search/status/<task_id>", methods=["GET"])
def get_task_status(task_id):
    task_result = search_task.AsyncResult(task_id)
    
    logger.info(f"Flask request for /search/status, with task id: {task_id}")
    
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
            "status": "Task completed successfully!"
        }
        if isinstance(task_result.result, str):
            response["result"] = json.loads(task_result.result)
        else:
            response["result"] = task_result.result
    return jsonify(response)

@main.route("/search/<task_id>", methods=["GET"]) # WIP
def get_cached_data(task_id):
    cached_data = fetch_from_cache(task_id)
    
    if cached_data is not None:
        return jsonify({"task_id": task_id, "data": cached_data}), 200
    else:
        return jsonify({"error": "Data not found"}), 404

@main.route("/sources", methods=["GET"])
def get_sources():
    sources = Source.query.all()
    
    result = []
    for source in sources:
        result.append({
            "name": source.name,
            "requires_api_key": source.requires_api_key,
            "api_key_configured": source.is_api_key_configured
        })
    
    return jsonify(result)

@main.route("/sources/<source_name>", methods=["POST"])
def set_api_key(source_name):
    api_key = request.json.get("api_key")
    
    source = Source.query.filter_by(name=source_name).first()
    if not source:
        return jsonify({"error": "Source not found"}), 404

    if not source.requires_api_key:
        return jsonify({"error": "This source does not required an API key"}), 400
    
    api_key_entry = APIKey.query.filter_by(source_name=source.name).first()
    if not api_key_entry:
        api_key_entry = APIKey(source_name=source.name)

    # Set and save the encrypted API key
    api_key_entry.set_key(api_key)
    db.session.add(api_key_entry)
    db.session.commit()

    return jsonify({"message": f"API key for {source_name} set successfully"}), 200
