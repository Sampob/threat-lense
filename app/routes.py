from datetime import datetime, timezone
import json

from app.tasks import search_task
from app.utils.indicator_type import is_valid_indicator
from app.utils.cache import fetch_from_cache
from app.utils.logger import setup_logger

from flask import jsonify, request

logger = setup_logger(__name__)

def configure_routes(app):
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            "error": "Bad Request",
            "message": f"The request could not be processed: {error}",
            "status_code": 400,
            "path": request.path,
            "timestamp": str(datetime.now(timezone.utc)),
            "hint": "Ensure all required parameters are provided and valid."
        }), 400
    
    @app.route("/search", methods=["GET"])
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

    @app.route("/search/status/<task_id>", methods=["GET"])
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
    
    @app.route("/search/<task_id>", methods=["GET"]) # WIP
    def get_cached_data(task_id):
        cached_data = fetch_from_cache(task_id)
        
        if cached_data is not None:
            return jsonify({"task_id": task_id, "data": cached_data}), 200
        else:
            return jsonify({"error": "Data not found"}), 404
