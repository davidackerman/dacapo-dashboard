from flask import render_template, request, redirect, url_for, jsonify
import dacapo
from dacapo.converter import converter
from dashboard.db import get_db

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
            db = get_db()
            db.add_optimizer(converter.unstructure(new_optimizer))
            return jsonify({"success": True})
        except Exception as e:
            raise(e)
            return jsonify({"success": False, "error": str(e)})

    fields = parse_fields(dacapo.configurables.Optimizer)
    _ = {"random_name": random.choice(dacapo.hash.ADJECTIVE_WORDLIST)}
    return render_template(
        "dacapo/forms/optimizer.html", fields=fields, id_prefix="optimizer"
    )
