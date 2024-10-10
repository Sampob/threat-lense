from app.tasks import search_task

from flask import jsonify, request
from celery.result import AsyncResult

def configure_routes(app):
    @app.route("/search", methods=["GET"])
    def search():
        indicator = request.json.get("indicator")
        # Start Celery task
        task = search_task.apply_async(args=[indicator])

        return jsonify({"task_id": task.id}), 202

    @app.route("/search/status/<task_id>", methods=["GET"])
    def get_task_status(task_id):
        task = AsyncResult(task_id)

        print(task)
        print(type(task))
        if task.state == "PENDING":
            return jsonify({"status": "Pending", "result": None}), 202
        elif task.state == "SUCCESS":
            return jsonify({"status": "Completed", "result": task.result}), 200
        elif task.state == "FAILURE":
            return jsonify({"status": "Failed", "error": str(task.info)}), 500
        else:
            return jsonify({"status": task.state, "result": None}), 202
