from flask import redirect

from .blue_print import bp
from dashboard.stores import get_stores

from dacapo.experiments import Run


def training_visualization_link(run):
    array_store = get_stores().array
    config_store = get_stores().config
    run_config = config_store.retrieve_run_config(run)
    run = Run(run_config)
    link = array_store._visualize_training(run)
    return link


@bp.route("/training/<run>", methods=["GET"])
def training(run):

    return redirect(training_visualization_link(run))
