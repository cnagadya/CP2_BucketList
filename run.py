"""Runner for the api"""
import os

from app import create_app


app,db = create_app(os.environ.get('FLASK_CONFIG','development'))
    #if no config set, use development
with app.app_context():
     db.create_all()


if __name__ == '__main__':
    app.run(port=8080)
