from dashboard.stores import get_stores

import dacapo
from dacapo.store.conversion_hooks import cls_fun
from .configurables import parse_fields


def get_checklist_data():

    config_store = get_stores().config
    context = {
        "tasks": config_store.retrieve_task_names(),
        "datasets": config_store.retrieve_dataset_names(),
        "architectures": config_store.retrieve_architecture_names(),
        "trainers": config_store.retrieve_trainer_names(),
    }
    return context


def get_config_name_to_fields_dict(class_name):

    config_name_to_fields_dict = {
        x: parse_fields(cls_fun(x))
        for x in getattr(dacapo.experiments,
                         class_name.lower()+"s").__dict__.keys()
        if x.endswith('Config')
        and cls_fun("object") not in cls_fun(x).__bases__
    }

    return config_name_to_fields_dict
