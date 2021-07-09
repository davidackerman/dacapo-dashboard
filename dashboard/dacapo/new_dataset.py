from flask import render_template, request, json, jsonify
import dacapo
from dacapo.store.converter import converter

from .blue_print import bp
from dashboard.stores import get_stores
from .helpers import get_config_name_to_fields_dict


@bp.route("/new_dataset", methods=["GET", "POST"])
def new_dataset():
    if request.method == "POST":
        try:
            data = request.json
            new_dataset = converter.structure(
                data, dacapo.configurables.Dataset)
            new_dataset.verify()
            db = get_stores()
            db.add_dataset(new_dataset)
            return jsonify({"success": True})
        except Exception as e:
            raise (e)
            return jsonify({"success": False, "error": str(e)})

    config_name_to_fields_dict = get_config_name_to_fields_dict("Dataset")
    return render_template(
        "dacapo/forms/dataset.html",
        fields=config_name_to_fields_dict,
        id_prefix="dataset",
        all_names=json.dumps(
            get_stores().config.retrieve_task_names()))
