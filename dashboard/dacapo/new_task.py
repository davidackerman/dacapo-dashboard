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
            db.add_task(converter.unstructure(new_task))
            return jsonify({"success": True})
        except Exception as e:
            raise (e)
            return jsonify({"success": False, "error": str(e)})

    fields = parse_fields(dacapo.configurables.Task)
    return render_template("dacapo/forms/task.html", fields=fields, id_prefix="task")
