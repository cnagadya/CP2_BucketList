from flask import Blueprint
from app.auth import auth_token

blist_api = Blueprint('api', __name__)


@blist_api.before_request
def before_request():
    pass


from . import bucketlists, items, session_management, errors
from app import auth
