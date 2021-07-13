from flask import render_template, request, json, jsonify

from .blue_print import bp
from dashboard.stores import get_stores

from .helpers import get_config_name_to_fields_dict


@bp.route("/new_architectures", methods=["GET", "POST"])
def new_architecture():
    if request.method == "POST":
        try:
            data = request.json
            get_stores().config.store_architecture_config(data)
            return jsonify({"success": True})
        except Exception as e:
            raise(e)
            return jsonify({"success": False, "error": str(e)})

    config_name_to_fields_dict = get_config_name_to_fields_dict("Architecture")
    return render_template(
        "dacapo/forms/architecture.html",
        fields=config_name_to_fields_dict,
        id_prefix="architecture",
        all_names=json.dumps(
            get_stores().config.retrieve_architecture_config_names()))
