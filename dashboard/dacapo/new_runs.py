from flask import json, render_template, request, jsonify

from dashboard.stores import get_stores
from .blue_print import bp
from .helpers import get_checklist_data

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
                {"config_type": "tasks",
                 "name": task_doc["name"],
                 "id": task_doc["id"]}
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
            assert (
                trainer_doc is not None
            ), f"Cannot find trainer with id: {trainer}"
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
        return render_template("dacapo/new_run.html", **context)

    if request.method == "POST":
        request_data = request.json
        run_component_ids = itertools.product(
            request_data["tasks"],
            request_data["datasets"],
            request_data["architectures"],
            request_data["trainers"],
        )

        config_store = get_stores().config
        run_config_names = config_store.retrieve_run_config_names()
        run_config_basenames = [n.split(":")[0] for n in run_config_names]
        new_runs = [
            {
                "name": '_'.join([task, dataset, architecture, trainer]),
                "task_config_name": task,
                "dataset_config_name": dataset,
                "architecture_config_name": architecture,
                "trainer_config_name": trainer
            }
            for task, dataset, architecture, trainer in run_component_ids
            if '_'.join([task, dataset, architecture, trainer])
            not in run_config_basenames
        ]

        return jsonify(new_runs)

    return render_template("dacapo/new_run.html")
