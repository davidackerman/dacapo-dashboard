import toml

from dashboard.db import get_db

import hashlib


def get_checklist_data():
    db = get_db()
    context = {
        "tasks": [(task["id"], task.get("name", "UGH")) for task in db.tasks.find({})],
        "datasets": [
            (dataset["id"], dataset.get("name", "UGH"))
            for dataset in db.datasets.find({})
        ],
        "models": [
            (model["id"], model.get("name", "UGH")) for model in db.models.find({})
        ],
        "optimizers": [
            (optimizer["id"], optimizer.get("name", "UGH"))
            for optimizer in db.optimizers.find({})
        ],
        "users": [user["username"] for user in db.users.find({})],
    }
    return context


def parse_config_form(form):
    data = {"name": form["name"]}
    parsed = toml.loads(form["content"])
    assert "name" not in parsed
    data.update(parsed)

    id_num = hashlib.md5(toml.dumps(data).encode("utf-8")).hexdigest()
    data["id"] = id_num
    return data
