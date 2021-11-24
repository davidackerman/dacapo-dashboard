import attr
from dashboard.stores import get_stores

import dacapo
from dacapo.store.conversion_hooks import cls_fun
from .configurables import parse_field, parse_fields

import importlib
import pkgutil


def get_checklist_data():

    config_store = get_stores().config
    context = {
        "tasks": config_store.retrieve_task_config_names(),
        "datasplits": config_store.retrieve_datasplit_config_names(),
        "architectures": config_store.retrieve_architecture_config_names(),
        "trainers": config_store.retrieve_trainer_config_names(),
    }
    return context


def get_config_name_to_fields_dict(class_name):
    if class_name == "DataSplitz":
        config_name_to_fields_dict = {}

        for datasplit_class_name in getattr(dacapo.experiments, "datasplits").__dict__.keys():
            # datasplits
            updated_value = 'typing.Union['
            if datasplit_class_name.endswith('DataSplitConfig') and cls_fun("object") not in cls_fun(datasplit_class_name).__bases__:
                current_dict = {}
                updated_value += f"dacapo.experiments.datasplits.{datasplit_class_name},"
                for field in attr.fields(cls_fun(datasplit_class_name)):
                    field_type = field.type
                    print("field_type",  field_type)

                    # try:
                    #     field_class_name = field_type.__name__
                    #     if field_class_name.endswith("Config"):
                    #         #then make it a choice of available configs
                        
                    #     current_dict[field.name] = {
                    #         'type': 'render_from_choice',}
                    # except AttributeError:
                    #     pass


                    print("field class name", field_type.__name__)
                    if not field.name.endswith("_config"):
                        current_dict[field.name] = parse_field(field)
                    else:
                        # datasets
                        choices = []
                        for dataset_class_name in getattr(dacapo.experiments.datasplits, "datasets").__dict__.keys():
                            if dataset_class_name.endswith('Config') and cls_fun("object") not in cls_fun(dataset_class_name).__bases__:

                                choices.append(dataset_class_name)
                                #print(parse_fields(cls_fun(dataset_class_name)))

                                # source, for now only arraysources
                                for array_class_name in getattr(dacapo.experiments.datasplits.datasets, "arrays").__dict__.keys():
                                    if array_class_name.endswith('Config') and cls_fun("object") not in cls_fun(array_class_name).__bases__:
                                        a=1
                                        #print(parse_fields(
                                        #    cls_fun(array_class_name)))

                        # updated_key = 'typing.Union['
                        # for x in getattr(dacapo.experiments.datasplits, "keys").__dict__.keys():
                        #     if x != "DataKey" and x.endswith('Key') and cls_fun("object") not in cls_fun(x).__bases__:
                        #         updated_key += f"dacapo.experiments.datasplits.keys.{x},"
                        # updated_key = updated_key[:-1]+"]"

                        # current_dict[field.name] = {
                        #     'type': 'dict', 'value': updated_value, 'key': updated_key}
                        current_dict[field.name] = {
                            'type': 'render_from_choice', 'config_name_to_fields_dict': {"a": {"name":  {"type":  "str"}},  "b": {"nbme":  {"type":  "str"}}}}
                config_name_to_fields_dict[datasplit_class_name] = current_dict
                # print("nonon")
                # updated_value = 'typing.Union['
                # updated_key = 'enum['
                # for x in getattr(dacapo.experiments.datasplits, "datasets").__dict__.keys():
                #     if x.endswith('Key') and cls_fun("object") not in cls_fun(x).__bases__:
                #         enum_instance = eval(
                #             f"dacapo.experiments.datasplits.keys.{x}")
                #         for e in enum_instance:
                #             updated_key += f"dacapo.experiments.datasplits.keys.{e},"
                # updated_key = updated_key[:-1]+"]"
                # print("updated_key", updated_key)
                # for source in ["train_configs", "validate_configs"]:
                #     config_name_to_fields_dict["DatasplitConfig"][
                #         source]['value'] = updated_value

                #     config_name_to_fields_dict["DatasplitConfig"][
                #         source]['key'] = "typing.Union[dacapo.experiments.datasplits.keys.ArrayKey,  dacapo.experiments.datasplits.keys.GraphKey]"

    elif class_name == "Dataset":

        config_name_to_fields_dict = {
            "DatasetConfig": parse_fields(cls_fun("DatasetConfig"))
        }
        # print(config_name_to_fields_dict)
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
            config_name_to_fields_dict["DatasetConfig"][
                source]['value'] = updated_value

            config_name_to_fields_dict["DatasetConfig"][
                source]['key'] = "typing.Union[dacapo.experiments.datasets.keys.ArrayKey,  dacapo.experiments.datasets.keys.GraphKey]"

    else:

        config_name_to_fields_dict = {
            x: parse_fields(cls_fun(x))
            for x in getattr(dacapo.experiments,
                             class_name.lower()+"s").__dict__.keys()
            if x.endswith('Config')
            and cls_fun("object") not in cls_fun(x).__bases__
        }
    print(config_name_to_fields_dict)
    return config_name_to_fields_dict


def get_evaluator_score_names(task_config_name):

    config_store = get_stores().config
    task_config = config_store.retrieve_task_config(task_config_name)
    task_instance = task_config.task_type(task_config)
    evaluator_scores = task_instance.evaluator.evaluate(
        None, None)
    evaluator_score_names = list(evaluator_scores.__dict__.keys())

    return evaluator_score_names


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

    raise AttributeError(
        f"No module in dacapo.experiments has attribute {configurable_name}")
