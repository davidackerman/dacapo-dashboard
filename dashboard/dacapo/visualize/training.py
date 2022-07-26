from flask import redirect, current_app, g
from flask_login.utils import login_required
from dacapo.store.local_array_store import LocalArrayStore

from .blue_print import bp

from dacapo.experiments import Run
from dacapo.options import Options

import subprocess
from pathlib import Path


def training_visualization_link(run, username):
    user_home = subprocess.check_output(f"echo ~{username}", shell=True).decode("utf-8").strip("\n")
    options = Options.instance()
    local_base_dir = Path(user_home, options.local_runs_base_dir)
    array_store = LocalArrayStore(local_base_dir)
    config_store = current_app.config["stores"].config
    run_config = config_store.retrieve_run_config(run)
    run = Run(run_config)
    link = array_store._visualize_training(run)
    return link


@bp.route("/training/<run>", methods=["GET"])
@login_required
def training(run):
    username = g.user_info["username"]

    return redirect(training_visualization_link(run, username))
