import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from elk_bot_db_manager import Messages
from config import config


class DataBaseHandler:
    def __init__(self):
        self.engine = db.create_engine(config.db_conn, echo=True)
        self.sesh = sessionmaker(bind=self.engine)

    def write_message(self, body, dttm):
        session = self.sesh()
        try:
            message = Messages(body, dttm)
            session.add(message)
            session.commit()
            session.refresh(message)
            return message.message_id
        finally:
            session.close()

    def get_message_by_id(self, message_id):
        session = self.sesh()
        try:
            return session.query(Messages).filter(Messages.message_id == message_id).first().body
        finally:
            session.close()
