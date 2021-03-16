from flask import render_template, request, redirect, url_for, jsonify
import dacapo
from dacapo.converter import converter

from .blue_print import bp
from .configurables import parse_fields
from dashboard.db import get_db

import random


@bp.route("/new_model", methods=["GET", "POST"])
def new_model():
    if request.method == "POST":
        try:
            data = request.json
            new_model = converter.structure(data, dacapo.configurables.Model)
            new_model.verify()
            db = get_db()
            db.add_model(converter.unstructure(new_model))
            return jsonify({"success": True})
        except Exception as e:
            raise(e)
            return jsonify({"success": False, "error": str(e)})

    fields = parse_fields(dacapo.configurables.Model)
    _ = {"random_name": random.choice(dacapo.hash.ADJECTIVE_WORDLIST)}
    return render_template("dacapo/forms/model.html", fields=fields, id_prefix="model")
