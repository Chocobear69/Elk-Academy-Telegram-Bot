import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from elk_bot_db_manager import Messages, Customers
from config import config


class DataBaseHandler:
    __slots__ = ('engine', 'sesh')

    def __init__(self):
        self.engine = db.create_engine(config.pg_conn, echo=True)
        self.sesh = sessionmaker(bind=self.engine)

    def write_message(self, message):
        session = self.sesh()
        try:
            message = Messages(message.from_user.id, message.chat.id, message.text)
            session.add(message)
            session.commit()
            #session.refresh(message)
        finally:
            session.close()

    def set_customer(self, message):
        session = self.sesh()
        try:
            customer = Customers(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                                 message.from_user.username)
            session.add(customer)
            session.commit()
        finally:
            session.close()

    def get_message_by_id(self, message_id):
        session = self.sesh()
        try:
            return session.query(Messages).filter(Messages.message_id == message_id).first().body
        finally:
            session.close()
