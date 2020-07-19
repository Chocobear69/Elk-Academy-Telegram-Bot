import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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
            customer = Customers(message.from_user.id, message.chat.id, message.from_user.first_name,
                                 message.from_user.last_name, message.from_user.username)
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
            session.query(Groups).filter(Groups.group_id == message).delete()
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

    def set_message_to_send(self, group_id, message_body, message_datetime, is_valid):
        session = self.sesh()
        try:
            message = MessagesToSend(group_id, message_body, message_datetime, is_valid)
            session.add(message)
            session.commit()
        finally:
            session.close()

    def get_messages_to_send(self):
        session = self.sesh()
        try:
            now = datetime.now()
            return [i for i in session.query(MessagesToSend).all() if i.message_datetime <= now and i.is_valid is True]
        finally:
            session.close()

    def delete_message_to_send(self, message_id):
        session = self.sesh()
        try:
            session.query(MessagesToSend).filter(MessagesToSend.message_id == message_id).delete()
            session.commit()
        finally:
            session.close()

    def get_groups(self):
        session = self.sesh()
        try:
            return {i.group_id: i.group_tag for i in session.query(Groups).all() if i.active_flag is True}
        finally:
            session.close()

    def get_admins(self):
        session = self.sesh()
        try:
            return {i.admin_id: i.admin_name for i in session.query(Admins).all()}
        finally:
            session.close()

    def set_admin(self, admin_name, admin_id):
        session = self.sesh()
        try:
            admin = Admins(admin_id, admin_name)
            session.add(admin)
            session.commit()
        finally:
            session.close()


if __name__ == '__main__':
    db = DataBaseHandler()
    gr = db.get_messages_to_send()
    print(gr)



