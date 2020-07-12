from config import config

from collections import namedtuple
from datetime import datetime
import pygsheets


class GoogleSheetsHandler:
    __slots__ = ('gsh_conn', 'events_sheet', 'groups_sheet', 'admins_sheet')

    def __init__(self):
        self.gsh_conn = pygsheets.authorize(service_file='client_secret.json')
        self.events_sheet = self.gsh_conn.open(config.sheet_name).worksheet_by_title(config.events_sheet_title)
        self.groups_sheet = self.gsh_conn.open(config.sheet_name).worksheet_by_title(config.group_sheet_title)
        self.admins_sheet = self.gsh_conn.open(config.sheet_name).worksheet_by_title(config.admins_sheet_title)

    def delete_event(self, index):
        self.events_sheet.delete_rows(index=index, number=1)

    def get_prepared_messages(self):
        now = datetime.now()
        fake_date = datetime(1970, 1, 1, 0, 0)
        message = namedtuple('Message', ['message_text', 'group_id'])
        records = self.events_sheet.get_all_records()
        suitable_records = dict()
        for index, record in enumerate(records):
            dttm = datetime.strptime(record.get('message_datetime', '01/01/1970 00:00'), config.datetime_format)
            if dttm != fake_date and dttm <= now:
                suitable_records[index + 2] = message(record['message_text'], record['group_name'])
        return suitable_records

    def get_groups(self):
        return {record['group_id']: record['group_tag'] for record in self.groups_sheet.get_all_records()}

    def get_admins(self):
        return {record['admin_id']: record['admin_name'] for record in self.admins_sheet.get_all_records()}

    def set_group(self, group_tag, group_id):
        chats_amount = len(self.get_groups())
        self.groups_sheet.append_table([group_tag, group_id], start='A' + str(chats_amount) if chats_amount else 'A2')

    def set_admin(self, admin_name, admin_id):
        chats_amount = len(self.get_admins())
        self.groups_sheet.append_table([admin_name, admin_id], start='A' + str(chats_amount) if chats_amount else 'A2')


if __name__ == '__main__':
    gsh_handler = GoogleSheetsHandler()
