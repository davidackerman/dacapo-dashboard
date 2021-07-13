from flask import render_template, request, json, jsonify
from dashboard.stores import get_stores

from .blue_print import bp
from .helpers import get_config_name_to_fields_dict


@bp.route("/new_trainer", methods=["GET", "POST"])
def new_trainer():
    if request.method == "POST":
        try:
            data = request.json
            get_stores().config.store_trainer_config(data)
            return jsonify({"success": True})
        except Exception as e:
            raise(e)
            return jsonify({"success": False, "error": str(e)})

    config_name_to_fields_dict = get_config_name_to_fields_dict("Trainer")
    return render_template(
        "dacapo/forms/trainer.html",
        fields=config_name_to_fields_dict,
        id_prefix="trainer",
        all_names=json.dumps(
            get_stores().config.retrieve_trainer_config_names()))
