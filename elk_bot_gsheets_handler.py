from config import config
from elk_bot_main import services
from datetime import datetime


def get_work_sheet(sheet, sheet_title):
    """

    :param sheet:
    :param sheet_title:
    :return:
    """
    return services.gsheets.open(sheet).worksheet_by_title(sheet_title)


def delete_record(work_sheet, index):
    """

    :param work_sheet:
    :param index:
    :return:
    """
    work_sheet.delete_rows(index=index, number=1)


def get_prepared_messages():
    """

    :return:
    """
    now = datetime.now()
    wsh = get_work_sheet(config.sheet_name, config.events_sheet_title)
    records = wsh.get_all_records()
    suitable_records = []
    for record in records:
        if record['message_datetime']:
            if datetime.strptime(record['message_datetime'], config.event_datetime_format) < now:
                suitable_records.append(record)
    return suitable_records


def get_chat_list():
    wsh = get_work_sheet(config.sheet_name, config.group_sheet_title)
    return [record['group_id'] for record in wsh.get_all_records()]


def set_group(group_name, group_id):
    wsh = get_work_sheet(config.sheet_name, config.group_sheet_title)
    chats_amount = len(get_chat_list())
    wsh.append_table([group_name, group_id], start='A' + str(chats_amount) if chats_amount else 'A2')


if __name__ == '__main__':
    set_group('Какая-то группа', 123)


