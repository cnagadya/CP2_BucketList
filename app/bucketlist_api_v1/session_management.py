from flask import jsonify, request
from app import db
from . import blist_api
from app.models import User
import validators


@blist_api.route('/auth/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email_add = request.json.get('email_add')
    password = request.json.get('password')

    if not username or not email_add or not password:
        return jsonify({"message": "Enter the username, email address and password to create account"}), 400
    if not validators.email(email_add):
        return jsonify({"message": "Email address should have 'email@example.com' format"}), 400
    if username.isdigit() or username.isspace() or password.isspace():
        return jsonify({"message": "Invalid value entered for username and / or password"})
    if User.query.filter_by(username=username.strip()).first():
        return jsonify({"message": "User with username '{}' already exists".format(username.strip())}), 409
    user = User(username=username.strip(), email_add=email_add.strip())
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"Successful Added": [{'username': user.username, 'email address': user.email_add}]}), 201


@blist_api.route('/auth/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({"message": "Enter the username and password"}), 400
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return jsonify({"message": "Invalid username or password"}), 403
    return jsonify({'Generated Token': user.generate_token()}), 201
