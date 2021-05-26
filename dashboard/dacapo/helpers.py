from dashboard.db import get_db
from bson.json_util import dumps

import hashlib


def get_checklist_data():
    db = get_db()
    context = {
        "tasks": [(task["id"], task.get("name", "UGH"), dumps(task, indent=2)) for task in db.tasks.find({})],
        "datasets": [
            (dataset["id"], dataset.get("name", "UGH"), dumps(dataset, indent=2))
            for dataset in db.datasets.find({})
        ],
        "models": [
            (model["id"], model.get("name", "UGH"), dumps(model, indent=2)) for model in db.models.find({})
        ],
        "optimizers": [
            (optimizer["id"], optimizer.get("name", "UGH"), dumps(optimizer, indent=2))
            for optimizer in db.optimizers.find({})
        ],
        "users": [user["username"] for user in db.users.find({})],
    }
    return context