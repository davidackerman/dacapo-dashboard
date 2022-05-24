from flask import (
    render_template,
    request,
    json,
    jsonify,
    url_for,
    redirect,
    current_app,
)

from .blue_print import bp
from dacapo.store.converter import converter
from dacapo.experiments.datasplits import DataSplitConfig

from .helpers import get_config_names
from .configs import CONFIGURABLES, CONFIGURABLE_FIELDS


@bp.route("/new_datasplit", methods=["GET", "POST"])
def new_datasplit():
    if request.method == "POST":
        try:
            data = request.json
            structured = converter.structure(data, DataSplitConfig)
            unstructured = converter.unstructure(structured)
            current_app.config["stores"].config.store_datasplit_config(data)
            return jsonify({"success": True})
        except Exception as e:
            raise (e)
            return jsonify({"success": False, "error": str(e)})

    config_names = get_config_names("DataSplit")
    config_fields = {name: CONFIGURABLE_FIELDS[name] for name in config_names}
    return render_template(
        "dacapo/forms/datasplit.html",
        fields=config_fields,
        id_prefix="datasplit",
        all_names=json.dumps(
            current_app.config["stores"].config.retrieve_datasplit_config_names()
        ),
    )

@bp.route("/visualize_datasplit", methods=["GET", "POST"])
def visualize_datasplit():
    pass

@bp.route("/visualize_datasplit/<state>", methods=["GET", "POST"])
def visualize_datasplit_from_existing(state):
    state = state.replace("%2F", "/")
    json_config = json.loads(state)
    config = converter.structure(json_config, DataSplitConfig)
    datasplit = config.datasplit_type(config)
    return redirect(datasplit._neuroglancer_link())


@bp.route("/new_datasplit/<state>", methods=["GET"])
def new_datasplit_from_existing(state):
    state = state.replace("%2F", "/")
    config_names = get_config_names("DataSplit")
    config_fields = {name: CONFIGURABLE_FIELDS[name] for name in config_names}
    return render_template(
        "dacapo/forms/datasplit.html",
        fields=config_fields,
        id_prefix="datasplit",
        all_names=json.dumps(
            current_app.config["stores"].config.retrieve_datasplit_config_names()
        ),
        value=state,
    )


@bp.route("/load_datasplit/<name>", methods=["GET"])
def load_datasplit(name):
    config = current_app.config["stores"].config.retrieve_datasplit_config(name)
    state_dict = converter.unstructure(config)
    print(state_dict)
    state = json.dumps(state_dict).replace("/", "%2F")

    return redirect(url_for("dacapo.new_datasplit_from_existing", state=state))
