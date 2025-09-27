from flask import Blueprint

alqaida_blueprint = Blueprint("alqaida_blueprint", __name__)
# Import routes to register endpoints on the blueprint
from .routes import encrypt  # noqa: E402,F401
from .routes import decrypt  # noqa: E402,F401
from .routes import api      # noqa: E402,F401
