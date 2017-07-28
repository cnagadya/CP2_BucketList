import os
import random
import string

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '../database/dev.db')

DEBUG = True
IGNORE_AUTH = True
SECRET_KEY = "".join(random.choice(
    string.ascii_uppercase + string.digits) for x in range(32))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + db_path
