class Config(object):
    SECRET_KEY = 'some-secret-value'
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost:5432/db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False


class DevelopmentConfig(Config):
    ENV = "development"
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    ENV = "testing"
    TESTING = True