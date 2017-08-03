from flask import Blueprint, request, jsonify

blist_api = Blueprint('api', __name__)


@blist_api.before_request
def before_request():
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({
            "message": "Content-Type should be application/json"
        }), 400


from . import bucketlists, items, session_management, errors
from app import auth
