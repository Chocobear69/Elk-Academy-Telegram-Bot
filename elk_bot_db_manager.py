from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

from config import config

engine = create_engine(config.db_conn, echo=True)
Base = declarative_base()


class Messages(Base):
    __tablename__ = 'messages'

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    body = Column(String)
    dttm = Column(DateTime)

    def __init__(self, body, dttm):
        self.body = body
        self.dttm = dttm


if __name__ == '__main__':
    Base.metadata.create_all(engine)
