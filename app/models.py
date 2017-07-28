"""Contains the different database models"""
from datetime import datetime
from dateutil import parser as datetime_parser
from dateutil.tz import tzutc
from flask import url_for, current_app, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)


class ValidationError(ValueError):
    pass


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True)
    password_hash = db.Column(db.String)
    email_add = db.Column(db.String)
    bucketlists = db.relationship('Bucketlist', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self, expires_in=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        return User.query.get(data['id'])


class Bucketlist(db.Model):
    __tablename__ = 'bucketlists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    items = db.relationship('Item', backref='bucketlist',
                            lazy='dynamic', cascade='all, delete-orphan')
    created = db.Column(db.DateTime, default=datetime.now())
    modified = db.Column(db.DateTime, default=datetime.now(),
                         onupdate=datetime.utcnow())
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))

    def import_data(self, data):
        try:
            self.name = data['name']
            self.owner = g.user.id
            # self.owner = data
            # self.created = datetime_parser.parse(
            # #     data['created']).astimezone(tzutc()).replace(tzinfo=None)
            # self.modified = datetime_parser.parse(
            #     data['modified']).astimezone(tzutc()).replace(tzinfo=None)
        except KeyError as e:
            raise ValidationError('Bucketlist not ' +
                                  e.args[0] + '. Crosscheck the name provided')
        return self


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey(
        'bucketlists.id'), index=True)
    name = db.Column(db.String, index=True)
    done = db.Column(db.Boolean, default=False)

    def import_data(self, data, bucketlist_id):
        try:
            self.name = data['name']
            if 'done' in data:
                self.done = data['done']
            self.list_id = bucketlist_id

        
        except KeyError as e:
            raise ValidationError(
                'Invalid item ' + e.args[0])
        return self
