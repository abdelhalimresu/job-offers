# Built-in
from datetime import datetime, timedelta
import hashlib

# Pip imports
from flask import current_app
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, ARRAY
import jwt

# Project imports
from api.db import db


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True)
    hashed_password = Column(String(32))

    def __repr__(self):
        return 'Id: {}, username: {}'.format(self.id, self.username)

    def check_password(self, password):
        return self.hashed_password == self._hash_password(password)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def create(self, password):
        self.hashed_password = self._hash_password(password)
        db.session.add(self)
        db.session.commit()

    def generate_token(self):
        payload = {
            'id': self.id,
            'username': self.username,
            'expires_at': str(datetime.utcnow() + timedelta(hours=current_app.config["JWT_TOKEN_VALIDITY"]))
        }
        return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm='HS256').decode()

    @staticmethod
    def _hash_password(password):
        return hashlib.md5(bytes(password, "utf-8")).hexdigest()


class Offer(db.Model):
    __tablename__ = 'offers'

    id = Column(Integer, primary_key=True)
    title = Column(String(32))
    description = Column(String(512))
    skills_list = Column(ARRAY(String))
    creation_date = Column(DateTime, default=datetime.utcnow)
    modification_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.now)
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
        db.session.commit()

    def create(self):
        db.session.add(self)
        db.session.commit()