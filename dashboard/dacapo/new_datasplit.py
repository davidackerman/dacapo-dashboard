from flask import render_template, request, json, jsonify

from .blue_print import bp
from dashboard.stores import get_stores
from .helpers import get_config_name_to_fields_dict


@bp.route("/new_datasplit", methods=["GET", "POST"])
def new_datasplit():
    if request.method == "POST":
        try:
            data = request.json
            get_stores().config.store_datasplit_config(data)
            return jsonify({"success": True})
        except Exception as e:
            raise (e)
            return jsonify({"success": False, "error": str(e)})

    config_name_to_fields_dict = get_config_name_to_fields_dict("DataSplit")
    return render_template(
        "dacapo/forms/datasplit.html",
        fields=config_name_to_fields_dict,
        id_prefix="datasplit",
        all_names=json.dumps(get_stores().config.retrieve_datasplit_config_names()),
    )


@bp.route("/new_datas_from_existing", methods=["GET"])
def new_dataset_from_existing():

    config_name_to_fields_dict = get_config_name_to_fields_dict("Dataset")
    print(config_name_to_fields_dict)
    dataset = get_stores().config.retrieve_dataset_config("dummy_dataset")
    dataset.__dict__["name"] = "dummy_dataset"
    print("\n\n\n\n dataset dict", dataset.__dict__, "\n\n\n\n")
    return render_template(
        "dacapo/forms/dataset_from_existing.html",
        fields=config_name_to_fields_dict,
        dataset_type="DummyDatasetConfig",
        dataset_to_copy=dataset.__dict__,
        id_prefix="dataset",
        all_names=json.dumps(get_stores().config.retrieve_datasplit_config_names()),
    )
