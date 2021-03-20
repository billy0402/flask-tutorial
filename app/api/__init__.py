from flask import Blueprint

api = Blueprint('api', __name__)

from . import (  # noqa:  F401
    authentication,
    users,
    posts,
    comments,
    errors,
)
