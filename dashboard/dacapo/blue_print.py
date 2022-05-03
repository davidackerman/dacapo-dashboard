from flask import Blueprint
from . import visualize
from . import configs

bp = Blueprint("dacapo", __name__, url_prefix="/dacapo")
bp.register_blueprint(visualize.bp)
bp.register_blueprint(configs.bp)
