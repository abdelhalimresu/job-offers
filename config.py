import os


class Config(object):
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:5432/{}'.format(
        os.environ.get("POSTGRES_USER"),
        os.environ.get("POSTGRES_PASSWORD"),
        os.environ.get("POSTGRES_HOST"),
        os.environ.get("POSTGRES_DB")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_VALIDITY = 24 # one day


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