from flask import render_template, request, jsonify
import dacapo
from dacapo.store.converter import converter

from .blue_print import bp
from dashboard.stores import get_stores

from .helpers import get_config_name_to_fields_dict


@bp.route("/new_architectures", methods=["GET", "POST"])
def new_architecture():
    if request.method == "POST":
        try:
            data = request.json
            new_architecture = converter.structure(
                data, dacapo.configurables.Architectures)
            new_architecture.verify()
            db = get_stores()
            db.add_architecture(new_architecture)
            return jsonify({"success": True})
        except Exception as e:
            raise(e)
            return jsonify({"success": False, "error": str(e)})

    config_name_to_fields_dict = get_config_name_to_fields_dict("Architecture")
    return render_template("dacapo/forms/architecture.html",
                           fields=config_name_to_fields_dict,
                           id_prefix="architecture")
