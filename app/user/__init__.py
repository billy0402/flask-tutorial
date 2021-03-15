from flask import Blueprint

user = Blueprint('user', __name__)

from . import views  # noqa: E402, F401
