from flask import render_template, request, redirect, url_for, jsonify
import dacapo
from dacapo.converter import converter

from .blue_print import bp
from .configurables import parse_fields
from dashboard.db import get_db


@bp.route("/new_task", methods=["GET", "POST"])
def new_task():
    if request.method == "POST":
        try:
            data = request.json
            new_task = converter.structure(data, dacapo.configurables.Task)
            new_task.verify()
            db = get_db()
            db.add_task(new_task)
            return jsonify({"success": True})
        except Exception as e:
            raise (e)
            return jsonify({"success": False, "error": str(e)})

    fields = parse_fields(dacapo.configurables.Task)
    print(fields)
    return render_template("dacapo/forms/task.html", fields=fields, id_prefix="task")

@bp.route("/new_task_from_existing", methods=["GET", "POST"])
def new_task_from_existing():
    if request.method == "POST":
        try:
            data = request.json
            new_task = converter.structure(data, dacapo.configurables.Task)
            new_task.verify()
            db = get_db()
            db.add_task(new_task)
            return jsonify({"success": True})
        except Exception as e:
            raise (e)
            return jsonify({"success": False, "error": str(e)})

    fields = parse_fields(dacapo.configurables.Task)
    task_to_copy = get_db().tasks.find_one({})
    print(task_to_copy)
    return render_template("dacapo/forms/task_from_existing.html", fields=fields, task_to_copy = task_to_copy, id_prefix="task")
