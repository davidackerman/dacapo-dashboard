from flask import render_template, request, json, jsonify, url_for, redirect

from .blue_print import bp
from dashboard.stores import get_stores
from dacapo.store.converter import converter

from .helpers import get_config_names
from .configs import CONFIGURABLES, CONFIGURABLE_FIELDS


@bp.route("/new_trainer", methods=["GET", "POST"])
def new_trainer():
    if request.method == "POST":
        try:
            data = request.json
            get_stores().config.store_trainer_config(data)
            return jsonify({"success": True})
        except Exception as e:
            raise (e)
            return jsonify({"success": False, "error": str(e)})

    config_names = get_config_names("Trainer")
    config_fields = {name: CONFIGURABLE_FIELDS[name] for name in config_names}
    return render_template(
        "dacapo/forms/trainer.html",
        fields=config_fields,
        id_prefix="trainer",
        all_names=json.dumps(get_stores().config.retrieve_trainer_config_names()),
    )


@bp.route("/new_trainer/<state>", methods=["GET"])
def new_trainer_from_existing(state):
    state = state.replace("%2F", "/")
    config_names = get_config_names("Trainer")
    config_fields = {name: CONFIGURABLE_FIELDS[name] for name in config_names}
    return render_template(
        "dacapo/forms/trainer.html",
        fields=config_fields,
        id_prefix="trainer",
        all_names=json.dumps(get_stores().config.retrieve_trainer_config_names()),
        value=state,
    )

@bp.route("/load_trainer/<name>", methods=["GET"])
def load_trainer(name):
    config = get_stores().config.retrieve_trainer_config(name)
    state_dict = converter.unstructure(config)
    state = json.dumps(state_dict).replace("/", "%2F")

    return redirect(url_for("dacapo.new_trainer_from_existing", state=state))