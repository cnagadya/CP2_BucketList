"""Contains all error handlers"""
from flask import jsonify
from . import blist_api

class ValidationError(ValueError):
    pass


@blist_api.errorhandler(ValidationError)
def bad_request(e):
    return jsonify({'message': e.args[0]}), 400


@blist_api.errorhandler(404)
def not_found(e):
    return jsonify({'message': 'Invalid resource URI',"Status Code":"404"}), 404

@blist_api.errorhandler(401)
def unauthorized_access(e):
    return jsonify({'message': 'Unauthorized Access! You need an authorization token to access this page'}), 401


@blist_api.errorhandler(405)
def method_not_supported(e):
    return jsonify({'message': 'Method is not supported'}), 405


@blist_api.app_errorhandler(500)
def internal_server_error(e):
    return jsonify({'message': e.args[0]}), 500
