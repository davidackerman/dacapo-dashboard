from flask import render_template, request, json, jsonify

from .blue_print import bp
from dashboard.stores import get_stores

from .helpers import get_config_names
from .configs import CONFIGURABLES, CONFIGURABLE_FIELDS


@bp.route("/new_architecture", methods=["GET", "POST"])
def new_architecture():
    if request.method == "POST":
        try:
            data = request.json
            get_stores().config.store_architecture_config(data)
            return jsonify({"success": True})
        except Exception as e:
            raise (e)
            return jsonify({"success": False, "error": str(e)})

    config_names = get_config_names("Architecture")
    config_fields = {name: CONFIGURABLE_FIELDS[name] for name in config_names}
    return render_template(
        "dacapo/forms/architecture.html",
        fields=config_fields,
        id_prefix="architecture",
        all_names=json.dumps(get_stores().config.retrieve_architecture_config_names()),
    )


@bp.route("/new_architecture/<state>", methods=["GET"])
def new_architecture_from_existing(state):
    state = state.replace("%2F", "/")
    config_names = get_config_names("Architecture")
    config_fields = {name: CONFIGURABLE_FIELDS[name] for name in config_names}
    return render_template(
        "dacapo/forms/architecture.html",
        fields=config_fields,
        id_prefix="architecture",
        all_names=json.dumps(get_stores().config.retrieve_architecture_config_names()),
        value=state,
    )
