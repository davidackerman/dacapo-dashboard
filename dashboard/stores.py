from flask import g

from dacapo.store import create_config_store,create_stats_store,create_weights_store

from collections import namedtuple

def get_stores():
    if "stores" not in g:
        g.stores = get_stores()

    return g.stores 


def close_stores(e=None):
    g.pop("stores", None)


def init_app(app):
    stores = get_stores()
    # app.config["MONGODB_SETTINGS"] = {
    #     "db": dacapo_db.db_name,
    #     "host": dacapo_db.db_host,
    # }

    # dacapo_db.init_app(app)


def get_stores():
    Stores = namedtuple('stores', ['config', 'stats','weights'])
    return Stores(create_config_store(), create_stats_store(), create_weights_store())    

