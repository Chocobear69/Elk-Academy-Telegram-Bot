from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

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
    dttm = Column(DateTime, default=datetime.now())

    def __init__(self, customer_id, group_id, body):
        self.customer_id = customer_id
        self.group_id = group_id
        self.body = body


class Customers(Base):
    pass
    __tablename__ = 'customers'
    __table_args__ = {'schema': 'dbo'}

    customer_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    customer_nickname = Column(String)

    def __init__(self, customer_id, first_name, last_name, nickname):
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.customer_nickname = nickname


if __name__ == '__main__':
    Base.metadata.create_all(engine)
