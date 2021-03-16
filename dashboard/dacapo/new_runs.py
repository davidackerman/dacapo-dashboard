from flask import render_template, request, jsonify

from dashboard.db import get_db
from .blue_print import bp
from .helpers import get_checklist_data

import itertools
from bson import Int64


@bp.route("/delete_configs", methods=["POST"])
def delete_configs():
    if request.method == "POST":
        db = get_db()
        request_data = request.json
        deleted_configs = []

        for task in request_data["tasks"]:
            task_doc = db.tasks.find_one({"id": task})
            assert task_doc is not None
            db.tasks.delete_one(task_doc)
            deleted_configs.append(
                {"config_type": "tasks", "name": task_doc["name"], "id": task_doc["id"]}
            )

        for dataset in request_data["datasets"]:
            dataset_doc = db.datasets.find_one({"id": dataset})
            assert dataset_doc is not None
            db.datasets.delete_one(dataset_doc)
            deleted_configs.append(
                {
                    "config_type": "datasets",
                    "name": dataset_doc["name"],
                    "id": dataset_doc["id"],
                }
            )

        for model in request_data["models"]:
            model_doc = db.models.find_one({"id": model})
            assert model_doc is not None
            db.models.delete_one(model_doc)
            deleted_configs.append(
                {
                    "config_type": "models",
                    "name": model_doc["name"],
                    "id": model_doc["id"],
                }
            )

        for optimizer in request_data["optimizers"]:
            optimizer_doc = db.optimizers.find_one({"id": optimizer})
            assert (
                optimizer_doc is not None
            ), f"Cannot find optimizer with id: {optimizer}"
            db.optimizers.delete_one(optimizer_doc)
            print(optimizer_doc["id"], optimizer)
            deleted_configs.append(
                {
                    "config_type": "optimizers",
                    "name": optimizer_doc["name"],
                    "id": str(optimizer_doc["id"]),
                }
            )
            print(jsonify(deleted_configs))

        return jsonify(deleted_configs)


@bp.route("/new_run", methods=["GET", "POST"])
def create_new_run():
    if request.method == "GET":
        context = get_checklist_data()
        return render_template("dacapo/new_run.html", **context)

    if request.method == "POST":
        request_data = request.json
        run_component_ids = itertools.product(
            request_data["tasks"],
            request_data["datasets"],
            request_data["models"],
            request_data["optimizers"],
        )

        db = get_db()
        new_runs = [
            {
                "task": db.tasks.find_one(
                    {"id": t}, projection={"id": True, "_id": False, "name": True}
                ),
                "dataset": db.datasets.find_one(
                    {"id": d}, projection={"id": True, "_id": False, "name": True}
                ),
                "model": db.models.find_one(
                    {"id": m}, projection={"id": True, "_id": False, "name": True}
                ),
                "optimizer": db.optimizers.find_one(
                    {"id": o}, projection={"id": True, "_id": False, "name": True}
                ),
            }
            for t, d, m, o in run_component_ids
            if db.runs.find_one({"task": t, "dataset": d, "model": m, "optimizer": o})
            is None
        ]
        print(new_runs)
        return jsonify(new_runs)

    return render_template("dacapo/new_run.html")