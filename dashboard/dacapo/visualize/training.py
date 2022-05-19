from flask import redirect, current_app

from .blue_print import bp

from dacapo.experiments import Run


def training_visualization_link(run):
    array_store = current_app.config["stores"].array
    config_store = current_app.config["stores"].config
    run_config = config_store.retrieve_run_config(run)
    run = Run(run_config)
    link = array_store._visualize_training(run)
    return link


@bp.route("/training/<run>", methods=["GET"])
def training(run):

    return redirect(training_visualization_link(run))
