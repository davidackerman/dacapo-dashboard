from flask import render_template, request, jsonify
import dacapo
from dacapo.store.converter import converter

from .blue_print import bp
from .configurables import parse_fields
from dashboard.stores import get_stores

import random


@bp.route("/new_dataset", methods=["GET", "POST"])
def new_dataset():
    if request.method == "POST":
        try:
            data = request.json
            new_dataset = converter.structure(data, dacapo.configurables.Dataset)
            new_dataset.verify()
            db = get_stores()
            db.add_dataset(new_dataset)
            return jsonify({"success": True})
        except Exception as e:
            raise (e)
            return jsonify({"success": False, "error": str(e)})

    fields = parse_fields(dacapo.configurables.Dataset)
    return render_template(
        "dacapo/forms/dataset.html", fields=fields, id_prefix="dataset"
    )
