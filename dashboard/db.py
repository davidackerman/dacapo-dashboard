from flask import g

from dacapo.store import MongoDbStore


def get_db():
    if "db" not in g:
        g.db = MongoDbStore()

    return g.db


def close_db(e=None):
    g.pop("db", None)


def init_app(app):
    dacapo_db = MongoDbStore()
    app.config["MONGODB_SETTINGS"] = {
        "db": dacapo_db.db_name,
        "host": dacapo_db.db_name,
    }

    # dacapo_db.init_app(app)