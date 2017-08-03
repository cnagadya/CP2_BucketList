import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)

    cfg = os.path.join(os.path.dirname(os.path.dirname(
        __file__)), 'config', config_name + '.py')
    app.config.from_pyfile(cfg)
    app.url_map.strict_slashes = False

    db.init_app(app)

    from .bucketlist_api_v1 import blist_api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app, db
