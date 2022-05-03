import dacapo.experiments

import importlib
import pkgutil


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


def get_configurables():
    submodules = import_submodules(dacapo.experiments)
    for _, submodule in submodules.items():
        for attr in dir(submodule):
            if attr.endswith("Config"):
                yield (attr, getattr(submodule, attr))

