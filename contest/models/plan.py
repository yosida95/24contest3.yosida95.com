#-*- coding: utf-8 -*-

import uuid
from datetime import date
from sqlalchemy import (
    Column,
    Boolean,
    Date,
    ForeignKey,
    Integer,
    Unicode,
    )
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from .user import User

Base = declarative_base()


class PlanList(Base):
    __tablename__ = 'plan_list'

    id = Column(Unicode(32),
            primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = Column(Integer, ForeignKey(User.id))
    user = relationship(User, backref=backref('plans'))
    date = Column(Date, default=date.today)

    def __init__(self, user, date):
        self.user = user
        self.date = date


class Plan(Base):
    __tablename__ = 'plans'

    id = Column(Unicode(32),
            primary_key=True, default=lambda: uuid.uuid4().hex)
    subject = Column(Unicode(255))
    done = Column(Boolean(), default=False)
    plan_list_id = Column(Unicode(32), ForeignKey(PlanList.id))
    plan_list = relationship(PlanList, backref=backref('plans'))
    deleted = Column(Boolean(), default=False)

    def __init__(self, subject):
        self.subject = subject

    def check_as_done(self):
        self.done = True

    def check_as_delete(self):
        self.deleted = True
