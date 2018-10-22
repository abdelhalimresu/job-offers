# Built-in
import os

# Pip imports
from flask import Flask
from flask_restplus import Api

# Project imports
from api.db import db
from api.resources import offers, users
from api.auth import auth


api = Api(version='1.0', title='Job offers',
    description='A Simple API for job offers', authorizations=auth
)

api.add_namespace(offers, path='/api/v1/users/<int:user_id>/offers')
api.add_namespace(users, path='/api/v1/users')


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    api.init_app(app)
    return app

if __name__ == '__main__':
    app = create_app(os.environ.get("APP_CONFIGURATION"))
    app.run(host="0.0.0.0")
