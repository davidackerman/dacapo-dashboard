import subprocess
from flask import json, render_template, g, current_app, request, jsonify
from flask_login.utils import login_required

from .blue_print import bp
from .helpers import get_checklist_data

import itertools

from dacapo.experiments import RunConfig


@bp.route("/delete_configs", methods=["POST"])
def delete_configs():
    if request.method == "POST":
        config_store = current_app.config["stores"].config
        request_data = request.json
        deleted_configs = []

        for task in request_data["tasks"]:
            task_doc = config_store.tasks.find_one({"name": task})
            assert task_doc is not None
            config_store.tasks.delete_one(task_doc)
            deleted_configs.append(
                {
                    "config_type": "tasks",
                    "name": task_doc["name"],
                }
            )

        for datasplit in request_data["datasplits"]:
            datasplit_doc = config_store.datasplits.find_one({"name": datasplit})
            assert datasplit_doc is not None
            config_store.datasplits.delete_one(datasplit_doc)
            deleted_configs.append(
                {
                    "config_type": "datasplits",
                    "name": datasplit_doc["name"],
                }
            )

        for architecture in request_data["architectures"]:
            architecture_doc = config_store.architectures.find_one(
                {"name": architecture}
            )
            assert architecture_doc is not None
            config_store.architectures.delete_one(architecture_doc)
            deleted_configs.append(
                {
                    "config_type": "architectures",
                    "name": architecture_doc["name"],
                }
            )

        for trainer in request_data["trainers"]:
            trainer_doc = config_store.trainers.find_one({"name": trainer})
            assert trainer_doc is not None, f"Cannot find trainer with id: {trainer}"
            config_store.trainers.delete_one(trainer_doc)
            deleted_configs.append(
                {
                    "config_type": "trainers",
                    "name": trainer_doc["name"],
                }
            )
            print(jsonify(deleted_configs))

        return jsonify(deleted_configs)


@bp.route("/new_run", methods=["GET", "POST"])
@login_required
def create_new_run():
    chargegroup = subprocess.getoutput(f'lsfgroup {g.user_info["username"]}')
    if request.method == "GET":
        context = get_checklist_data()
        context["chargegroup"] = chargegroup
        context["compute_queue"] = "gpu_rtx"
        context["username"] = g.user_info["username"]
        return render_template("dacapo/new_run.html", **context)

    if request.method == "POST":
        request_data = request.json
        run_component_ids = itertools.product(
            request_data["tasks"],
            request_data["datasplits"],
            request_data["architectures"],
            request_data["trainers"],
        )

        config_store = current_app.config["stores"].config
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
