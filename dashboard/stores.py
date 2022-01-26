from flask import g

from dacapo.store import (
    create_config_store,
    create_stats_store,
    create_weights_store,
    create_array_store,
)

from collections import namedtuple


def get_stores():
    if "stores" not in g:
        g.stores = get_stores_as_named_tuple()

    return g.stores


def close_stores(e=None):
    g.pop("stores", None)


def init_app(app):
    # TODO: What needs to go here
    stores = get_stores_as_named_tuple()
    # app.config["MONGODB_SETTINGS"] = {
    #     "db": dacapo_db.db_name,
    #     "host": dacapo_db.db_host,
    # }

    # dacapo_db.init_app(app)


def get_stores_as_named_tuple():
    Stores = namedtuple("stores", ["config", "stats", "weights", "array"])
    return Stores(
        create_config_store(),
        create_stats_store(),
        create_weights_store(),
        create_array_store(),
    )
