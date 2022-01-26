from flask import json, render_template, request, jsonify

from dashboard.stores import get_stores
from .blue_print import bp
from .helpers import get_checklist_data, datasplit_visualization_link

import itertools

from dacapo.experiments import RunConfig


@bp.route("/delete_configs", methods=["POST"])
def delete_configs():
    if request.method == "POST":
        config_store = get_stores().config
        request_data = request.json
        deleted_configs = []

        for task in request_data["tasks"]:
            task_doc = config_store.retrieve_task_config(task)
            assert task_doc is not None
            db.tasks.delete_one(task_doc)
            deleted_configs.append(
                {"config_type": "tasks", "name": task_doc["name"], "id": task_doc["id"]}
            )

        for datasplit in request_data["datasplits"]:
            datasplit_doc = db.datasplits.find_one({"id": datasplit})
            assert datasplit_doc is not None
            db.datasplits.delete_one(datasplit_doc)
            deleted_configs.append(
                {
                    "config_type": "datasplits",
                    "name": datasplit_doc["name"],
                    "id": datasplit_doc["id"],
                }
            )

        for architecture in request_data["architectures"]:
            architecture_doc = db.architectures.find_one({"id": architecture})
            assert architecture_doc is not None
            db.architectures.delete_one(architecture_doc)
            deleted_configs.append(
                {
                    "config_type": "architectures",
                    "name": architecture_doc["name"],
                    "id": architecture_doc["id"],
                }
            )

        for trainer in request_data["trainers"]:
            trainer_doc = db.trainers.find_one({"id": trainer})
            assert trainer_doc is not None, f"Cannot find trainer with id: {trainer}"
            db.trainers.delete_one(trainer_doc)
            print(trainer_doc["id"], trainer)
            deleted_configs.append(
                {
                    "config_type": "trainers",
                    "name": trainer_doc["name"],
                    "id": str(trainer_doc["id"]),
                }
            )
            print(jsonify(deleted_configs))

        return jsonify(deleted_configs)


@bp.route("/new_run", methods=["GET", "POST"])
def create_new_run():
    if request.method == "GET":
        context = get_checklist_data()
        datasplits = context.pop("datasplits")
        datasplits = [
            (datasplit, datasplit_visualization_link(datasplit))
            for datasplit in datasplits
        ]
        context["datasplits"] = datasplits
        return render_template("dacapo/new_run.html", **context)

    if request.method == "POST":
        request_data = request.json
        run_component_ids = itertools.product(
            request_data["tasks"],
            request_data["datasplits"],
            request_data["architectures"],
            request_data["trainers"],
        )

        config_store = get_stores().config
        run_config_names = config_store.retrieve_run_config_names()
        run_config_basenames = [n.split(":")[0] for n in run_config_names]
        new_runs = [
            {
                "name": "_".join([task, datasplit, architecture, trainer]),
                "task_config_name": task,
                "datasplit_config_name": datasplit,
                "architecture_config_name": architecture,
                "trainer_config_name": trainer,
            }
            for task, datasplit, architecture, trainer in run_component_ids
            if "_".join([task, datasplit, architecture, trainer])
            not in run_config_basenames
        ]

        return jsonify(new_runs)

    return render_template("dacapo/new_run.html")
