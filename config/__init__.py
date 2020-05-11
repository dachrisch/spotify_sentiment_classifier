# https://hackersandslackers.com/configure-flask-applications/


class DevelopmentConfig(object):
    DEBUG = True
    TESTING = True


class TestingConfig(object):
    DEBUG = False
    TESTING = True


class ProductionConfig(object):
    DEBUG = False
    TESTING = False
