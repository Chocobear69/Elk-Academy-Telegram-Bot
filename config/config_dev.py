token = '883751338:AAEFIPpzP4F-awZDO6-8K9uHhq97XlXWx5U'

"""sheets.google connection"""
sheet_name = 'elk-academy-shedule'
events_sheet_title = 'events'
group_sheet_title = 'groups'
admins_sheet_title = 'admins'

"""Data base connection"""
pg_conn = 'postgresql+psycopg2://postgres:2wsxCDE#@192.168.1.31/elk_academy'
pg_conn_manual = 'dbname=elk_academy user=postgres password=2wsxCDE#'
#db_conn = 'sqlite:///sqlite3.db'

"""Schedule"""
datetime_format = '%d/%m/%Y %H:%M'
scheduler_interval_min = 10

info_chat_id = ''
info_message_template = 'MESSAGE ID:\n' \
                        '{message_id}\n' \
                        'MESSAGE TEXT:\n' \
                        '{message}\n'\
                        'to next groups:\n' \
                        '{groups}'
first_message = 'Hi!\n' \
                'I am Samantha bot and i will help you to separate the chaff from the grain\n' \
                'This is commands to use:\n' \
                '/start - Start tracking messages with tags in this group\n' \
                '/remove - Stop tracking group\n' \
                '/hello - Introduce yourself to me\n'


"""Super User"""
sup_user_id = []
