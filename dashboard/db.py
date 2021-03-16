from flask import g
from flask_mongoengine import MongoEngine

from dacapo.store import MongoDbStore


def get_db():
    if "db" not in g:
        g.db = MongoDbStore()

    return g.db


def close_db(e=None):
    g.pop("db", None)


def init_db():
    get_db()


def init_app(app):
    db = MongoEngine()

    dacapo_db = MongoDbStore()
    app.config["MONGODB_SETTINGS"] = {
        "db": dacapo_db.db_name,
        "host": dacapo_db.db_name,
    }

    db.init_app(app)