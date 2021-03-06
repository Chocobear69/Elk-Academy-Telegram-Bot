from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from datetime import datetime
from config import config

engine = create_engine(config.pg_conn, echo=True)
Base = declarative_base()


class Messages(Base):
    __tablename__ = 'messages'
    __table_args__ = {'schema': 'dbo'}

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer)
    group_id = Column(Integer)
    body = Column(String)
    dttm = Column(DateTime, default=func.now())

    def __init__(self, customer_id, group_id, body):
        self.customer_id = customer_id
        self.group_id = group_id
        self.body = body


class Customers(Base):
    __tablename__ = 'customers'
    __table_args__ = {'schema': 'dbo'}

    customer_id = Column(Integer, primary_key=True)
    group_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    customer_nickname = Column(String)

    def __init__(self, customer_id, group_id, first_name, last_name, nickname):
        self.customer_id = customer_id
        self.group_id = group_id
        self.first_name = first_name
        self.last_name = last_name
        self.customer_nickname = nickname


class Groups(Base):
    __tablename__ = 'groups'
    __table_args__ = {'schema': 'dbo'}

    group_id = Column(Integer, primary_key=True)
    group_tag = Column(String)
    active_flag = Column(Boolean, default=True)

    def __init__(self, group_id, group_tag):
        self.group_id = group_id
        self.group_tag = group_tag
        self.active_flag = True


class MessagesToSend(Base):
    __tablename__ = 'messages_to_send'
    __table_args__ = {'schema': 'dbo'}

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer)
    message_body = Column(String)
    is_valid = Column(Boolean)
    message_datetime = Column(DateTime, nullable=True)

    def __init__(self, group_id, message_body, message_datetime, is_valid=True):
        self.group_id = group_id
        self.message_body = message_body
        self.message_datetime = message_datetime
        self.is_valid = is_valid


class Admins(Base):
    __tablename__ = 'admins'
    __table_args__ = {'schema': 'dbo'}

    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    admin_name = Column(String)

    def __init__(self, admin_id, admin_name):
        self.admin_id = admin_id
        self.admin_name = admin_name


if __name__ == '__main__':
    Base.metadata.create_all(engine)
