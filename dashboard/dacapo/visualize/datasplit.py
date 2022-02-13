from flask import redirect

from .blue_print import bp
from dashboard.stores import get_stores


def datasplit_visualization_link(datasplit: str):
    config_store = get_stores().config
    datasplit_config = config_store.retrieve_datasplit_config(datasplit)
    datasplit = datasplit_config.datasplit_type(datasplit_config)
    link = datasplit._neuroglancer_link()
    return link


@bp.route("/datasplit/<datasplit>", methods=["GET"])
def datasplit(datasplit):

    return redirect(datasplit_visualization_link(datasplit))
