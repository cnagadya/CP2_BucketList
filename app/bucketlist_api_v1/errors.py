"""Contains all error handlers"""
from flask import jsonify
from . import blist_api


@blist_api.app_errorhandler(400)
def bad_request(e):
    return jsonify({
        'message': "Either Required Paremeters \
        are missing or invalid data has been entered"
    }), 400


@blist_api.app_errorhandler(404)
def not_found(e):
    return jsonify({
        'message': 'Invalid resource URI', "Status Code": "404"
    }), 404


@blist_api.app_errorhandler(401)
def unauthorized_access(e):
    return jsonify({
        'message': 'Unauthorized Access! You need an \
         authorization token to access this page'
    }), 401


@blist_api.app_errorhandler(405)
def method_not_supported(e):
    return jsonify({'message': 'Method is not supported'}), 405


@blist_api.app_errorhandler(500)
def internal_server_error(e):
    return jsonify({'message': "Internal server error"}), 500
