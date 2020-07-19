import schedule
import time
from datetime import datetime

from config import config

from elk_bot_db_handler import DataBaseHandler
from elk_bot_gsheets_handler import GoogleSheetsHandler

db_handler = DataBaseHandler()
gsh_handler = GoogleSheetsHandler()


def main():
    events = gsh_handler.get_events()
    for i in events:
        try:
            message_datetime = datetime.strptime(i['message_datetime'], config.datetime_format)
        except:
            message_datetime = None
        if message_datetime:
            db_handler.set_message_to_send(i['group_id'], i['message_text'], message_datetime, True)
        elif not message_datetime:
            db_handler.set_message_to_send(i['group_id'], i['message_text'], message_datetime, False)
    gsh_handler.clear_events()


if __name__ == '__main__':
    schedule.every(1).minutes.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
