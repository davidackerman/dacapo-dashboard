from flask import url_for

import attr
from dashboard.stores import get_stores

import dacapo
from dacapo.experiments import Run
from dacapo.experiments.datasplits import DataSplit
from dacapo.store.conversion_hooks import cls_fun
from .configurables import parse_field, parse_fields

import importlib
import pkgutil


def get_checklist_data():

    config_store = get_stores().config
    context = {
        "tasks": config_store.retrieve_task_config_names(),
        "datasplits": [
            (datasplit, url_for("dacapo.visualize.datasplit", datasplit=datasplit))
            for datasplit in config_store.retrieve_datasplit_config_names()
        ],
        "architectures": config_store.retrieve_architecture_config_names(),
        "trainers": config_store.retrieve_trainer_config_names(),
    }
    return context


def get_config_names(class_name):

    config_names = [
        x
        for x in getattr(dacapo.experiments, class_name.lower() + "s").__dict__.keys()
        if x.endswith("Config") and cls_fun("object") not in cls_fun(x).__bases__
    ]
    return config_names


def get_evaluator_score_names(task_config_name):

    config_store = get_stores().config
    task_config = config_store.retrieve_task_config(task_config_name)
    task_instance = task_config.task_type(task_config)
    evaluator_score_names = task_instance.evaluator.criteria

    return evaluator_score_names


def import_submodules(package, recursive=True):
    """Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + "." + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


def get_configurable(configurable_name):
    submodules = import_submodules(dacapo.experiments)
    for _, submodule in submodules.items():
        if hasattr(submodule, configurable_name):
            return getattr(submodule, configurable_name)

    raise AttributeError(
        f"No module in dacapo.experiments has attribute {configurable_name}"
    )
