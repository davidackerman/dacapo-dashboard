from flask import Blueprint
from . import visualize

bp = Blueprint("dacapo", __name__, url_prefix="/dacapo")
bp.register_blueprint(visualize.bp)
