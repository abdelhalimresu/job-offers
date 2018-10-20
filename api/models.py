# Pip imports
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, String, Integer, ForeignKey

# Project imports
from api.db import db


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(20))
    password = Column(String(20))

    def __repr__(self):
        return 'Id: {}, username: {}'.format(self.id, self.username)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        db.session.commit()

    def create(self):
        db.session.add(self)
        db.session.commit()