from flask import render_template, request, redirect, url_for, jsonify
import dacapo
from dacapo.store.converter import converter
from dashboard.stores import get_stores

from .blue_print import bp
from .configurables import parse_fields
from .helpers import get_config_name_to_fields_dict

import random


@bp.route("/new_trainer", methods=["GET", "POST"])
def new_trainer():
    if request.method == "POST":
        try:
            data = request.json
            new_trainer = converter.structure(
                data, dacapo.configurables.trainer)
            print(new_trainer)
            new_trainer.verify()
            db = get_stores()
            db.add_trainer(new_trainer)
            return jsonify({"success": True})
        except Exception as e:
            raise(e)
            return jsonify({"success": False, "error": str(e)})

    config_name_to_fields_dict = get_config_name_to_fields_dict("Trainer")
    return render_template(
        "dacapo/forms/trainer.html",
        fields=config_name_to_fields_dict,
        id_prefix="trainer"
    )
