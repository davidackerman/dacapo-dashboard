from flask import render_template, request, jsonify, g, current_app

from .blue_print import bp
from .helpers import get_checklist_data

from datetime import datetime


@bp.route("/results", methods=["GET", "POST"])
def get_results():
    if request.method == "GET":
        context = get_checklist_data()
        context.update(
            {
                "scores": set(
                    [
                        key
                        for run in db.runs.find({})
                        for validation_score in db.validation_scores.find(
                            {"run": run["id"]}
                        ).limit(1)
                        for key in validation_score["parameter_scores"]["0"]["scores"][
                            "sample"
                        ].keys()
                    ]
                ),
            }
        )
        return render_template("dacapo/results.html", **context)
    elif request.method == "POST":
        db = g.stores
        request_data = request.json
        runs = [
            {
                "name": run["hash"].split(":")[0],
                "repetition": run["repetition"],
                "trained_iterations": db.training_stats.find(
                    {"run": run["id"]}
                ).count(),
                "started": datetime.fromtimestamp(run["started"])
                if run["started"] is not None
                else "NA",
                "task": run["task_config"],
                "data": "NA",
                "architecture": run["architecture_config"],
                "trainer": run["trainer_config"],
            }
            for run in db.runs.find(
                {"task_config": {"$in": [x.strip() for x in request_data["tasks"]]}}
            )
        ]
        return jsonify(runs)

    return render_template("dacapo/results.html")
