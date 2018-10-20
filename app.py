# Built-in
import os

# Pip imports
from flask import Flask
from flask_restplus import Api

# Project imports
from api.db import db


api = Api(version='1.0', title='Job offers',
    description='A Simple API for job offers'
)


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    api.init_app(app)
    return app


app = create_app(os.environ.get("APP_CONFIGURATION"))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
