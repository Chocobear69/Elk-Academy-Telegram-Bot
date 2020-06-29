token = ''

"""sheets.google connection"""
sheet_name = 'elk-academy-shedule'
events_sheet_title = 'events'
group_sheet_title = 'groups'
admins_sheet_title = 'admins'

"""Data base connection"""
pg_conn = 'postgresql+psycopg2://postgres:2wsxCDE#@192.168.1.31/elk_academy'
#db_conn = 'sqlite:///sqlite3.db'

"""Schedule"""
datetime_format = '%d/%m/%Y %H:%M'
scheduler_interval_min = 1

info_chat_id = ''
info_message_template = 'MESSAGE ID:\n' \
                        '{message_id}\n' \
                        'MESSAGE TEXT:\n' \
                        '{message}\n'\
                        'to next groups:\n' \
                        '{groups}'
first_message = 'Hi!\n'


"""Super User"""
sup_user_id = []
