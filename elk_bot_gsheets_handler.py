from config import config

from datetime import datetime
import pygsheets


class GoogleSheetsHandler:
    def __init__(self):
        self.gsh_conn = pygsheets.authorize(service_file='client_secret.json')
        self.events_sheet = self.gsh_conn.open(config.sheet_name).worksheet_by_title(config.events_sheet_title)
        self.groups_sheet = self.gsh_conn.open(config.sheet_name).worksheet_by_title(config.group_sheet_title)

    def delete_event(self, index):
        """

        :param index:
        :return:
        """
        self.events_sheet.delete_rows(index=index, number=1)

    def get_prepared_messages(self):
        """

        :return:
        """
        now = datetime.now()
        records = self.events_sheet.get_all_records()
        suitable_records = dict()
        for record in records:
            if record['message_datetime']:
                if datetime.strptime(record['message_datetime'], config.event_datetime_format) < now:
                    suitable_records[record['message_text']] = records.index(record) + 2
        return suitable_records

    def get_chat_list(self):
        return [record['group_id'] for record in self.groups_sheet.get_all_records()]

    def set_group(self, group_name, group_id):
        chats_amount = len(self.get_chat_list())
        self.groups_sheet.append_table([group_name, group_id], start='A' + str(chats_amount) if chats_amount else 'A2')


if __name__ == '__main__':
    pass


