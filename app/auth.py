"""Contains all the authentication & authorization related features"""
from flask import jsonify, g, current_app, request
from flask_httpauth import HTTPTokenAuth, HTTPBasicAuth
from app.models import User
from app import db

auth_token = HTTPTokenAuth(scheme="Bearer")
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    g.user = User.query.filter_by(username=username).first()
    if g.user is None:
        return False
    return g.user.verify_password(password)

# @auth.error_handler
# def unauthorised():
#     return jsonify({"status": 401, "message": "unauthorised access. You need to sign in"})


@auth_token.verify_token
def verify_token(token):
    if not token:
        return False
    user = User.verify_token(token=token)
    if user is None:
        return False
    g.user = User.query.filter_by(id=user.id).first()
    return True

@auth.verify_password
def verify_auth_token(token, unused):
    if current_app.config.get('IGNORE_AUTH'):
        g.user = User.query.get(1)
    else:
        g.user = User.verify_token(token)
    return g.user is not None


@auth_token.error_handler
def invalid_token():
    return jsonify({'message': 'Enter a valid authentication token code'}), 401

