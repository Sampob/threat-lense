from app.tasks import search_task
from app.utils.logger import app_logger

from flask import jsonify, request

def configure_routes(app):
    @app.route("/search", methods=["GET"])
    def search():
        indicator = request.json.get("indicator")
        
        app_logger.info(f"Flask request for /search, with indicator: '{indicator}")
        
        # Start Celery task
        task = search_task.delay(indicator)

        return jsonify({
            "task_id": task.id,
            "status_url": f"/search/status/{task.id}"
        }), 202

    @app.route("/search/status/<task_id>", methods=["GET"])
    def get_task_status(task_id):
        task_result = search_task.AsyncResult(task_id)
        
        app_logger.info(f"Flask request for /search/status, with task id: '{task_id}")
        
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
        else:
            response = {
                "state": task_result.state,
                "result": task_result.result
            }
        return jsonify(response)