from flask import render_template, request, redirect, url_for, jsonify
import dacapo
from dacapo.store.converter import converter
from dashboard.stores import get_stores

from .blue_print import bp
from .configurables import parse_fields

import random


@bp.route("/new_optimizer", methods=["GET", "POST"])
def new_optimizer():
    if request.method == "POST":
        try:
            data = request.json
            new_optimizer = converter.structure(data, dacapo.configurables.Optimizer)
            print(new_optimizer)
            new_optimizer.verify()
            db = get_stores()
            db.add_optimizer(new_optimizer)
            return jsonify({"success": True})
        except Exception as e:
            raise(e)
            return jsonify({"success": False, "error": str(e)})

    fields = parse_fields(dacapo.configurables.Optimizer)
    return render_template(
        "dacapo/forms/optimizer.html", fields=fields, id_prefix="optimizer"
    )
