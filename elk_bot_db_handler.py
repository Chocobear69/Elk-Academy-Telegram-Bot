import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from elk_bot_db_manager import *
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

    def set_group(self, message):
        session = self.sesh()
        try:
            group = Groups(message.chat.id, message.text)
            session.add(group)
            session.commit()
            return 1
        except Exception as e:
            return 0
        finally:
            session.close()

    def set_customer(self, message):
        session = self.sesh()
        try:
            customer = Customers(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                                 message.from_user.username)
            session.add(customer)
            session.commit()
            return 1
        except Exception as e:
            return 0
        finally:
            session.close()

    def delete_group(self, message):
        session = self.sesh()
        try:
            Groups.query.filter(Groups.group_id == message).delete()
            session.commit()
        finally:
            session.close()

    def get_messages_by_date(self, date):
        now = date.today()
        session = self.sesh()
        try:
            return session.query(Messages).filter(db.func.date(Messages.dttm) == now)
        finally:
            session.close()

    def set_message_to_send(self, group_id, message):
        session = self.sesh()
        try:
            message = MessagesToSend(group_id, message)
            session.add(message)
            session.commit()
        finally:
            session.close()
