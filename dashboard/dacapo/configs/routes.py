from flask import request, jsonify, render_template, url_for

from dacapo.store.converter import converter

from .blue_print import bp
from .helpers import get_configurables
from .field_parsing import parse_fields

import json
import urllib.parse

# parse configurables once and reuse
CONFIGURABLES = {k: v for k, v in get_configurables()}
CONFIGURABLE_FIELDS = {k: parse_fields(v) for k, v in get_configurables()}


def get_name(cls):
    try:
        return cls.__name__
    except AttributeError:
        return str(cls)


@bp.route("create/<config_type>", methods=["POST"])
def create(config_type):
    config_class = CONFIGURABLES[config_type]
    try:
        config_data = request.json
        if "__type__" not in config_data:
            config_data["__type__"] = config_type
        config = converter.structure(config_data, config_class)
        valid, message = config.verify()
        return jsonify({"success": valid, "message": message})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@bp.route("verify/<config_type>", methods=["POST"])
def verify(config_type):
    config_class = CONFIGURABLES[config_type]
    try:
        config_data = request.json
        if "__type__" not in config_data:
            config_data["__type__"] = config_type
        config = converter.structure(config_data, config_class)
        valid, message = config.verify()

    except Exception as e:
        valid, message = False, str(e)

    print(valid, message)
    return jsonify({"success": valid, "message": message})


@bp.route("json/", methods=["GET"])
def all_json():
    return render_template(
        "dacapo/configs/configurables.html",
        configurables=[
            (c, url_for("dacapo.configs.config_json", name=c))
            for c in CONFIGURABLE_FIELDS
        ],
    )


@bp.route("json/<name>", methods=["GET"])
def config_json(name: str):
    return jsonify(CONFIGURABLE_FIELDS[name])


@bp.route("form/", methods=["GET"])
def all_form():
    return render_template(
        "dacapo/configs/configurables.html",
        configurables=[
            (c, url_for("dacapo.configs.config_form", name=c))
            for c in CONFIGURABLE_FIELDS
        ],
    )


@bp.route("form/<name>", methods=["GET"])
def config_form(name: str):
    return render_template(
        "dacapo/configs/configurable_form.html",
        fields=CONFIGURABLE_FIELDS[name],
        id_prefix=name,
        all_names=["test"],
        config_type=name,
    )


@bp.route("form/<string:name>/<string:state>/", methods=["GET"])
def stateful_config_form(name: str, state: str):
    state = state.replace("%2F", "/")
    return render_template(
        "dacapo/configs/configurable_form.html",
        fields=CONFIGURABLE_FIELDS[name],
        id_prefix=name,
        all_names=["test"],
        config_type=name,
        value=state,
    )


@bp.route("/configurable")
def configurable():
    raise Exception("This is a placeholder and shouldn't be called!")


@bp.route("/configurable/<name>/<id_prefix>", methods=["GET"])
def specific_configurable(name: str, id_prefix: str):

    fields = CONFIGURABLE_FIELDS[name]

    html = render_template(
        "dacapo/configs/configurable.html",
        fields=fields,
        id_prefix=id_prefix,
        all_names=["test"],
    )
    return jsonify({"html": html})
