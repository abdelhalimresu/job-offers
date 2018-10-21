# Built-in
from datetime import datetime

# Pip imports
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, ARRAY

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


class Offer(db.Model):
    __tablename__ = 'offers'

    id = Column(Integer, primary_key=True)
    title = Column(String(32))
    description = Column(String(512))
    skills_list = Column(ARRAY(String))
    creation_date = Column(DateTime, default=datetime.utcnow)
    modification_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))

    # Relationships
    user = relationship("User", backref=backref('offers', lazy='dynamic'))

    def __repr__(self):
        return 'Id: {}, title: {}'.format(self.id, self.title)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        # Update modification date
        self.modification_date = datetime.utcnow
        db.session.commit()

    def create(self):
        db.session.add(self)
        db.session.commit()