token = ''

"""Proxy connection"""
ip = ''
port = ''

"""sheets.google connection"""
sheet_name = 'elk-academy-shedule'
events_sheet_title = 'events'
group_sheet_title = 'groups'
admins_sheet_title = 'admins'

"""Data base connection"""
db_conn = 'sqlite:///sqlite3.db'

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
first_message = 'Привет, {user_name}!\n' \
                'Команды:\n' \
                'add - Добавляет группу в список групп для рассылки\n' \
                'alert - Рассылает сообщение от администратора во все группы\n'


"""Super User"""
sup_user_id = []
