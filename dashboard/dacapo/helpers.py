from dashboard.stores import get_stores
from bson.json_util import dumps

import hashlib


def get_checklist_data():
    config_store = get_stores().config
    context = {
        "tasks": config_store.retrieve_all_task_configs(),
        "datasets": config_store.retrieve_all_dataset_configs(),
        "architectures": config_store.retrieve_all_architecture_configs(),
        "trainers": config_store.retrieve_all_trainer_configs(),
        "users": [''] #TODO: users...user["username"] for user in config_store.users.find({})],
    }
    return context