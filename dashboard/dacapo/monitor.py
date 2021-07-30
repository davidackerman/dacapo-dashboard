from flask import render_template, request, jsonify
from dacapo.experiments import RunConfig

from dashboard.stores import get_stores
from .blue_print import bp
from .helpers import get_checklist_data
import dacapo

import itertools


@bp.route("/runs", methods=["GET", "POST"])
def get_runs():
    if request.method == "GET":
        context = get_checklist_data()
        return render_template("dacapo/runs.html", **context)
    if request.method == "POST":
        request_data = request.json
        run_component_ids = itertools.product(
            request_data["tasks"],
            request_data["datasets"],
            request_data["architectures"],
            request_data["trainers"],
        )

        config_store = get_stores().config
        runs = [
            {"id": run["id"],
                "execution_details": run["execution_details"],
                "task": config_store.retrieve_task_config(task),
                "dataset": config_store.retrieve_dataset_config(dataset),
                "architecture": config_store.retrieve_architecture_config(
                    architecture),
                "trainers": config_store.retrieve_trainer_config(trainer)
             }

            for task, dataset, architecture, trainer in run_component_ids
            if (run := config_store.retrieve_run_config(
                '_'.join([task, dataset, architecture, trainer])))
            is not None
        ]
        return jsonify(runs)

    return render_template("dacapo/runs.html")


@ bp.route("/apply_config", methods=["GET"])
def apply_config():
    if request.method == "GET":
        return render_template("dacapo/apply_config.html")

    return render_template("dacapo/apply_config.html")


@ bp.route("/start_runs", methods=["POST"])
def start_runs():
    if request.method == "POST":
        config_json = request.json
        config_store = get_stores().config
        for run in config_json.pop("runs"):
            for i in range(int(config_json["repetitions"])):
                run_config_name = ("_").join([run["task_config_name"],
                                             run["dataset_config_name"],
                                             run["architecture_config_name"],
                                             run["trainer_config_name"]])+f":{i}"

                run_config = RunConfig(
                    name=run_config_name,
                    task_config=config_store.retrieve_task_config(
                        run["task_config_name"]),
                    architecture_config=config_store.retrieve_architecture_config(
                        run["architecture_config_name"]),
                    trainer_config=config_store.retrieve_trainer_config(
                        run["trainer_config_name"]),
                    dataset_config=config_store.retrieve_dataset_config(
                        run["dataset_config_name"]),
                    repetition=1,
                    num_iterations=int(config_json["num_iterations"]),
                    snapshot_interval=int(config_json["snapshot_interval"]),
                    validation_score='IoU',
                    validation_score_minimize=False
                )

                config_store.store_run_config(run_config)
                dacapo.train(run_config_name)

    return jsonify({"success": True})
