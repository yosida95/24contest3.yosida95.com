#-*- coding: utf-8 -*-

from hashlib import sha1
from random import random
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Unicode,
    )
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True)
    handle = Column(Unicode(10), unique=True)
    email = Column(Unicode(100))
    joined = Column(DateTime(), default=datetime.utcnow)

    def __init__(self, handle, email):
        self.handle = handle
        self.email = email


class Login(Base):
    __tablename__ = 'login'

    id = Column(Integer, autoincrement=True, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), unique=True)
    user = relationship(User, backref=backref('login', uselist=False))
    password = Column(Unicode(40))
    last_authenticated = Column(DateTime)

    def __init__(self, user):
        self.user = user

    def set_password(self, password):
        salt = sha1(unicode(random())).hexdigest()[:3]
        self.password = u'%s+%s' % (salt, sha1(salt + password).hexdigest())

    def authenticate(self, password):
        salt, hashed = self.password.split('+')
        result = sha1(salt + password).hexdigest() == hashed
        if result:
            self.last_authenticated = datetime.utcnow()
        return result
