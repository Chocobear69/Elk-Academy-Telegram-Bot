import schedule
import time
import psycopg2
from elk_bot_db_handler import DataBaseHandler


db_handler = DataBaseHandler()
pg_conn = psycopg2.connect("dbname='elk_academy' user='postgres' host='192.168.1.31' password='2wsxCDE#'")


def get_messages():
    cursor = pg_conn.cursor()
    try:
        cursor.execute(
            """
                SELECT g.group_id, c.customer_nickname, m.customer_id
                FROM dbo.groups g
                        INNER JOIN
                            (SELECT group_id,
                                    customer_id, 
                                    first_name, 
                                    last_name, 
                                    customer_nickname 
                             FROM dbo.customers) c
                                ON g.group_id = c.group_id
                        LEFT JOIN
                            (SELECT DISTINCT customer_id,
                                    group_id, dttm
                             FROM dbo.messages
                             WHERE date(dttm) = CURRENT_DATE) m
                                ON c.customer_id = m.customer_id
                                    AND g.group_id = m.group_id    
                WHERE g.active_flag IS True;
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()


def divide_good_and_bad(messages):
    messages_to_send = dict()
    for message in messages:
        if message[0] not in messages_to_send:
            messages_to_send[message[0]] = {
                'good_boys': [],
                'bad_boys': [],
            }
        if message[2]:
            messages_to_send[message[0]]['good_boys'].append(message[1])
        else:
            messages_to_send[message[0]]['bad_boys'].append(message[1])
    return messages_to_send


def make_messages(divided):
    message_template = 'Hi, Everyone!\n' \
                       'This is the daily message statistics:\n' \
                       '**Good Boys:**\n' \
                       '{}\n' \
                       '**Bad Boys:**\n' \
                       '{}'
    messages_to_send = dict()
    for group, persons in divided.items():
        good_boys = '\n'.join(persons['good_boys'])
        bad_boys = '\n'.join(persons['bad_boys'])
        messages_to_send[group] = message_template.format(good_boys, bad_boys)
    return messages_to_send


def send_messages(messages):
    for group, message in messages.items():
        db_handler.set_message_to_send(group, message)


def main():
    messages = get_messages()
    divided = divide_good_and_bad(messages)
    messages_to_send = make_messages(divided)
    send_messages(messages_to_send)


if __name__ == '__main__':
    schedule.every().day.at("21:00").do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)

