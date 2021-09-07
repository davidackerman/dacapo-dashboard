from flask import render_template, request, json, jsonify
import dacapo
from dacapo.store.converter import converter

from .blue_print import bp
from .configurables import parse_fields
from dashboard.stores import get_stores

from .helpers import get_config_name_to_fields_dict


@bp.route("/new_task", methods=["GET", "POST"])
def new_task():
    if request.method == "POST":
        try:
            data = request.json
            get_stores().config.store_task_config(data)
            return jsonify({"success": True})
        except Exception as e:
            raise (e)
            return jsonify({"success": False, "error": str(e)})

    config_name_to_fields_dict = get_config_name_to_fields_dict("Task")
    return render_template(
        "dacapo/forms/task.html",
        fields=config_name_to_fields_dict,
        id_prefix="task",
        all_names=json.dumps(
            get_stores().config.retrieve_task_config_names()))


@bp.route("/new_task_from_existing", methods=["GET", "POST"])
def new_task_from_existing():
    if request.method == "POST":
        try:
            data = request.json
            new_task = converter.structure(data, dacapo.configurables.Task)
            new_task.verify()
            db = get_stores()
            db.add_task(new_task)
            return jsonify({"success": True})
        except Exception as e:
            raise (e)
            return jsonify({"success": False, "error": str(e)})

    config_name_to_fields_dict = get_config_name_to_fields_dict("Task")
    print(config_name_to_fields_dict)
    task = get_stores().config.retrieve_task_config("dummy_task")
    print(task.__dict__)
    return render_template("dacapo/forms/task_from_existing.html",
                           fields=config_name_to_fields_dict,
                           task_type="DummyTaskConfig",
                           task_to_copy=task.__dict__,
                           id_prefix="task",
                           all_names=json.dumps(
                               get_stores().config.retrieve_task_config_names()))
