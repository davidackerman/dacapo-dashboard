from dacapo.store import (
    create_config_store,
    create_stats_store,
    create_weights_store,
    create_array_store,
)

from collections import namedtuple

from dashboard.user_store import UserStore


def get_or_create_stores_as_named_tuple():
    Stores = namedtuple("stores", ["users", "config", "stats", "weights", "array"])
    return Stores(
        UserStore(),
        create_config_store(),
        create_stats_store(),
        create_weights_store(),
        create_array_store(),
    )
