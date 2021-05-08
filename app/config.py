import os


class Configuration(object):
    DEBUG = True
    APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/data.db' % APPLICATION_DIR
    SITE_WIDTH = 1140
    ADMIN_PASSWORD = 'secret'
    SECRET_KEY = 'shhh, secret!'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
