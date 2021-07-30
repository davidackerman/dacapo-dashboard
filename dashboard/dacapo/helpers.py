from dashboard.stores import get_stores

import dacapo
from dacapo.store.conversion_hooks import cls_fun
from .configurables import parse_fields

import importlib
import pkgutil


def get_checklist_data():

    config_store = get_stores().config
    context = {
        "tasks": config_store.retrieve_task_config_names(),
        "datasets": config_store.retrieve_dataset_config_names(),
        "architectures": config_store.retrieve_architecture_config_names(),
        "trainers": config_store.retrieve_trainer_config_names(),
    }
    return context


def get_config_name_to_fields_dict(class_name):

    if class_name == "Dataset":

        config_name_to_fields_dict = {
            "DatasetConfig": parse_fields(cls_fun("DatasetConfig"))
        }
        print(config_name_to_fields_dict)
        updated_value = 'typing.Union['
        updated_key = 'enum['
        for x in getattr(dacapo.experiments, "datasets").__dict__.keys():
            if x.endswith('SourceConfig') and cls_fun("object") not in cls_fun(x).__bases__:
                updated_value += f"dacapo.experiments.datasets.{x},"
        updated_value = updated_value[:-1]+"]"

        for x in getattr(dacapo.experiments, "datasets").__dict__.keys():
            if x.endswith('Key') and cls_fun("object") not in cls_fun(x).__bases__:
                enum_instance = eval(f"dacapo.experiments.datasets.keys.{x}")
                for e in enum_instance:
                    updated_key += f"dacapo.experiments.datasets.keys.{e},"
        updated_key = updated_key[:-1]+"]"

        for source in ["train_sources", "validate_sources", "predict_sources"]:
            element = config_name_to_fields_dict["DatasetConfig"][
                source]['value']

            config_name_to_fields_dict["DatasetConfig"][
                source]['value'] = updated_value

            config_name_to_fields_dict["DatasetConfig"][
                source]['key'] = "typing.Union[dacapo.experiments.datasets.keys.ArrayKey,  dacapo.experiments.datasets.keys.GraphKey]"

        print(element)
        print(updated_value)
        print(updated_key)
    else:

        config_name_to_fields_dict = {
            x: parse_fields(cls_fun(x))
            for x in getattr(dacapo.experiments,
                             class_name.lower()+"s").__dict__.keys()
            if x.endswith('Config')
            and cls_fun("object") not in cls_fun(x).__bases__
        }

    return config_name_to_fields_dict


def import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results


def get_configurable(configurable_name):
    submodules = import_submodules(dacapo.experiments)
    for _, submodule in submodules.items():
        if hasattr(submodule, configurable_name):
            return getattr(submodule, configurable_name)

    raise AttributeError(f"No module in dacapo.experiments has attribute {configurable_name}")
