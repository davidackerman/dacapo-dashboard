import importlib
from dacapo.store.conversion_hooks import cls_fun
import attr
from funlib.geometry import Coordinate

from .blue_print import bp
from typing import get_origin, get_args, Union
from enum import Enum
from pathlib import Path

from collections import OrderedDict


def get_name(cls):
    try:
        return cls.__name__
    except AttributeError:
        return str(cls)


def handle_simple_types(field_type, metadata):
    """
    simple types are types that don't really need any javascript.
    int -> text input, number
    str -> text input, string
    float -> text input, (bounds, step metadata)
    """
    simple_types = {int: "int", str: "str", float: "float", bool: "bool", Path: "path"}
    return {
        "type": simple_types[field_type],
        "help_text": metadata.get("help_text"),
        "default": metadata.get("default"),
    }


def handle_special_cases(field_type, metadata):
    """
    simple types are types that don't really need any javascript.
    int -> text input, number
    str -> text input, string
    float -> text input, (bounds, step metadata)
    """
    if field_type == Coordinate:
        return {
            "type": "list",
            "help_text": metadata.get("help_text"),
            "element": get_field_type(int, {}),
        }


def handle_enum(field_type, metadata):
    return {
        "type": "enum",
        "choices": [e.value for e in field_type],
        "help_text": metadata.get("help_text"),
    }


def is_optional(field_type):
    # field must be a Union with 2 options, one of which is None
    return (
        get_origin(field_type) == Union
        and len(get_args(field_type)) == 2
        and get_args(field_type)[1] == type(None)
    )


def is_choice(field_type):
    """
    A union over multiple types
    """
    return get_origin(field_type) == Union and not is_optional(field_type)


def is_expandable(field_type):
    return get_origin(field_type) in (list, dict, tuple, set)


def handle_complex_types(field_type, metadata):
    complex_types = {
        list: "list",
        dict: "dict",
        Union: "union",
        tuple: "tuple",
        Enum: "enum",
    }
    if is_optional(field_type):
        # add optional tag to field data and recurse 1 layer down
        field_data = {"optional": True}
        field_data.update(get_field_type(get_args(field_type)[0], metadata))
        return field_data
    elif is_choice(field_type):
        choices = [x.__name__ for x in get_args(field_type)]
        field_data = {
            "type": "choice",
            "choices": choices,
            "help_text": metadata.get("help_text"),
        }
        return field_data
    elif get_origin(field_type) == dict:
        key, value = get_args(field_type)
        key = get_name(key)
        value = get_name(value)
        field_data = {
            "type": "dict",
            "key": key,
            "value": value,
            "help_text": metadata.get("help_text"),
        }
        return field_data
    elif get_origin(field_type) == list:
        elements = get_args(field_type)
        assert len(elements) == 1
        element = elements[0]

        field_data = {
            "type": "list",
            "help_text": metadata.get("help_text"),
            "element": get_field_type(element, {}),
        }
        return field_data
    elif get_origin(field_type) == tuple:
        args = [get_field_type(x, {}) for x in get_args(field_type)]
        if "__default" in metadata and metadata["__default"] is not attr.NOTHING:
            for i, default in enumerate(metadata["__default"]):
                args[i]["default"] = default
        field_data = {
            "type": "tuple",
            "help_text": metadata.get("help_text"),
            "args": args,
        }
        return field_data
    else:
        raise RuntimeError(f"GOT UNSUPPORTED COMPLEX TYPE: {field_type}")


def get_field_type(field_type, metadata):
    simple_types = set([int, str, float, bool, Path])
    complex_types = set([list, dict, Union, tuple,])
    # behaves as list of ints for now.
    # TODO: allow users to specify dimensionality, all coordinates will be expected
    # to use that same dimensionality
    special_cases = set([Coordinate])
    if get_name(field_type).endswith("Config"):
        # A Config used as a type should always be a parent class
        # i.e. ArrayConfig, DatasetConfig, etc. Never a specific Config
        # such as ZarrArrayConfig.
        return {
            "type": "config_choice",
            "help_text": metadata.get("help_text"),
            "options": parse_subclasses(field_type),
        }
    elif field_type in simple_types:
        return handle_simple_types(field_type, metadata)

    elif get_origin(field_type) in complex_types:
        return handle_complex_types(field_type, metadata)

    elif field_type in special_cases:
        return handle_special_cases(field_type, metadata)

    elif issubclass(field_type, Enum):
        return handle_enum(field_type, metadata)

    raise ValueError(
        f"Unsupported type: {field_type}, "
        f"origin: {get_origin(field_type)}, "
        f"args: {get_args(field_type)}"
    )


def parse_subclasses(base_class):
    module_split = base_class.__module__.split(".")
    parent_module = ".".join(module_split[:-2])
    module = module_split[-2]

    config_name_to_fields_dict = {}
    for class_name in getattr(
        importlib.import_module(parent_module), module
    ).__dict__.keys():
        if (
            class_name.endswith("Config")
            and cls_fun("object") not in cls_fun(class_name).__bases__
        ):
            config_name_to_fields_dict[class_name] = {}
    return config_name_to_fields_dict


def parse_field(field):
    field_data = {}
    metadata = dict(**field.metadata)
    metadata["__default"] = field.default

    field_data.update(get_field_type(field.type, metadata))
    field_data["default"] = field.default if field.default is not attr.NOTHING else None
    if isinstance(field_data["default"], attr.Factory):
        field_data["default"] = field_data["default"].factory()
    return field_data


def parse_fields(configurable):
    field_data = OrderedDict(
        (field.name, parse_field(field)) for field in attr.fields(configurable)
    )
    return field_data
