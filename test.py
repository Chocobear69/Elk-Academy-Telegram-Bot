from glowbot_init import bot
from csv_handler import get_csv_data, insert_into_notified_events_list, get_event_list, clean_up_notified_events
from telebot import types
from config import config
from datetime import datetime, timedelta
from ast import literal_eval
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

events = get_event_list()
users = get_csv_data(config.csv_files['users'])
zones = get_csv_data(config.csv_files['zones'])
custom_message = {}


@bot.message_handler(commands=['chat'])
def check_chat_id(message):
    bot.reply_to(message, message.chat.id)


@bot.message_handler(commands=['restart_events'])
def restart_events(message):
    if check_permission(message):
        clean_up_notified_events()


def check_permission(message):
    """
    Проверяет админ ли пользователь
    :param message: сообщение для проверки
    :return: boolean
    """
    administrators = [val.user.id for val in bot.get_chat_administrators(message.chat.id)]
    return message.chat.id == config.adm_chat_id and message.from_user.id in administrators


def send_message_to_users(message):
    """
    Оповестить всех пользователей бота
    :param message: сообщение для пользователей
    :type message: str
    """
    for i in users:
        try:
            bot.send_message(i['id'], message)
        except Exception as e:
            print(e)


def string_to_datetime(dttm):
    """
    Преобразует строку в datetime
    :type: str
    :return: datetime
    """
    return datetime.strptime(dttm, config.datetime_format)


def send_zone_buttons(chat_id, user_id):
    """
    Отправляет в чат список кнопок с зонами
    :type chat_id: char
    :type user_id: int
    """
    keyboard = types.InlineKeyboardMarkup()

    #Кнопка отмены
    abort_callback_data = {
        'data': 4,
        'l': 1,
        'uid': user_id
    }
    callback_button = types.InlineKeyboardButton(text='Отмена', callback_data=str(abort_callback_data))
    keyboard.add(callback_button)

    #Кнопки с зонами
    for row in zones:
        callback_dict = {
            'id': row['id'],
            'data': 1,
            'uid': user_id
        }
        callback_button = types.InlineKeyboardButton(text=row['name'], callback_data=str(callback_dict))
        keyboard.add(callback_button)
    bot.send_message(chat_id, 'Выберите зону', reply_markup=keyboard)


def send_event_buttons(chat_id, user_id, callback_data):
    """
    Отправляет в чат список кнопок с событиями
    :type chat_id: char
    :type user_id: int
    :param callback_data: информация по зоне
    :type callback_data: dict
    """
    zone_names = {row['id']: row['name'] for row in zones}

    keyboard = types.InlineKeyboardMarkup()

    #Кнопка возвращения назад
    back_callback_data = {
        'data': 4,
        'l': 2,
        'uid': user_id
    }
    callback_button = types.InlineKeyboardButton(text='Назад', callback_data=str(back_callback_data))
    keyboard.add(callback_button)

    #Кнопки с событиями
    for row in events:
        if callback_data['id'] == row['zone_id']:
            callback_dict = {
                'id': row['id'],
                'zid': callback_data['id'],
                'data': 2,
                'uid': user_id
            }
            callback_button = types.InlineKeyboardButton(text=row['name'], callback_data=str(callback_dict))
            keyboard.add(callback_button)
    text = '{zone}\nВыберите событие'.format(zone=zone_names[callback_data['id']])
    bot.send_message(chat_id, text, reply_markup=keyboard)


def send_decision_buttons(chat_id, user_id, callback_data, back_flag=True):
    """
    Отправляет в чат список из кнопок да/нет/назад
    :type chat_id: str
    :type user_id: str
    :param callback_data: информация по событию
    :type callback_data: dict
    :param back_flag: флаг необходимости кнопки "назад"
    :type back_flag: boolean
    """
    event_names = {row['id']: row['name'] for row in events}

    keyboard = types.InlineKeyboardMarkup()
    if back_flag:
    #Кнопка возвращения назад
        back_callback_data = {
            'id': callback_data['zid'],
            'data': 4,
            'l': 3,
            'uid': user_id
        }
        callback_button = types.InlineKeyboardButton(text='Назад', callback_data=str(back_callback_data))
        keyboard.add(callback_button)


    #Остальные кнопки
    affirmative_callback_data = {
        'id': callback_data['id'],
        'data': 3,
        'l': 'yes',
        'uid': user_id,
    }
    if callback_data['id'] == -1:
        text = 'Отправить?'
        affirmative_callback_data['mid'] = callback_data['mid']
    else:
        text = '{text}.\nОтправить?'.format(text=event_names[callback_data['id']])

    callback_button = types.InlineKeyboardButton(text='Да', callback_data=str(affirmative_callback_data))
    keyboard.add(callback_button)

    negative_callback_data = {
        'id': callback_data['id'],
        'data': 3,
        'l': 'no',
        'uid': user_id
    }
    callback_button = types.InlineKeyboardButton(text='Нет', callback_data=str(negative_callback_data))
    keyboard.add(callback_button)
    bot.send_message(chat_id, text, reply_markup=keyboard)


@bot.message_handler(commands=['notify'])
def send_zones_button_list_by_command(message):
    """
    По команде /notify выводит список зон
    :param message: сообщение /notify
    """
    if check_permission(message):
        send_zone_buttons(user_id=message.from_user.id, chat_id=message.chat.id)


@bot.callback_query_handler(func=lambda call: 'uid' in call.data)
def button_call_handler(call):
    """
    Обрабатывает нажатие на кнопки в чате
    :param call: объект callbackquery который возвращается при нажатии на кнопку
    """
    callback_data = literal_eval(call.data)
    button_types = config.button_types
    if callback_data['uid'] == call.from_user.id or callback_data['uid'] == 0:

        if button_types[callback_data['data']] == 'zone':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_event_buttons(call.message.chat.id, call.from_user.id, callback_data)
            return

        if button_types[callback_data['data']] == 'event':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_decision_buttons(call.message.chat.id, call.from_user.id, callback_data)
            return

        if button_types[callback_data['data']] == 'decision':

            if callback_data['l'] == 'yes':
                if callback_data['id'] == -1:
                    text = custom_message[callback_data['mid']]
                else:
                    events_text = {row['id']: row['text'] for row in events}
                    text = events_text[callback_data['id']]
                bot.delete_message(call.message.chat.id, call.message.message_id)
                send_message_to_users(text)
                bot.send_message(call.message.chat.id, 'Отправил!')
                if callback_data['id'] != -1:
                    insert_into_notified_events_list(callback_data['id'])
                return

            if callback_data['l'] == 'no':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, 'Хорошего дня!')
                return

        if button_types[callback_data['data']] == 'back':

            if button_types[callback_data['l']] == 'zone':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                bot.send_message(call.message.chat.id, 'Хорошего дня!')
                return
            elif button_types[callback_data['l']] == 'event':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                send_zone_buttons(call.message.chat.id, callback_data['uid'])
                return
            elif button_types[callback_data['l']] == 'decision':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                send_event_buttons(call.message.chat.id, call.from_user.id, callback_data)
                return


@bot.message_handler(commands=['alert'])
def send_custom_message_to_users_by_command(message):
    """
    Для определенного чата(adm) и только для админов чата
    Обрабатывает команду alert - передает сообщение админа и передает в функцию alert_all
    :param message: сообщение alert
    """
    if check_permission(message):
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id, 'Что передать?', reply_markup=markup)
        bot.register_for_reply(msg, custom_message_handler, alert_owner_id=message.from_user.id)


def custom_message_handler(message, alert_owner_id):
    """
    Обрабатывает кастомное сообщение от пользователя
    :param message: сообщние от пользователя
    :param alert_owner_id: айди пользователя, который ввел команду /alert
    :type alert_owner_id: int
    """
    if message.from_user.id == alert_owner_id:

        if message.content_type == 'text':
            custom_message[message.message_id] = message.text
            callback_data = {
                'id': -1,
                'mid': message.message_id
            }
            send_decision_buttons(message.chat.id, message.from_user.id, callback_data=callback_data, back_flag=False)
        else:
            bot.send_message(message.chat.id, 'Могу отправить только текст(')
            bot.register_for_reply(message.reply_to, custom_message_handler, alert_owner_id)

    else:
        bot.register_for_reply(message.reply_to, custom_message_handler, alert_owner_id)


def events_handler_auto(event):
    """
    Обрабатывает события, для которых пришло время автоматической нотификации
    :param event: информация по событию
    :type event: dict
    """
    send_message_to_users(event['text'])
    insert_into_notified_events_list(event['id'])
    event['is_notify_flag'] = 1


def events_handler_manual(event):
    """
    Обрабатывает события, для которых пришло время ручной нотификации
    :param event: информация по событию
    :type event: dict
    """
    callback_data = {
        'id': event['id']
    }
    text = '{event} скоро начнется'.format(event=event['name'])
    bot.send_message(config.adm_chat_id, text)
    send_decision_buttons(config.adm_chat_id, 0, callback_data, back_flag=False)
    event['is_notify_flag'] = 1


def reminder():
    """
    Напоминает о событиях, которые должны наступить в ближайшее время
    """
    now = datetime.now()
    do_not_notify_border = now - timedelta(hours=config.do_not_notify_interval_hours)
    for row in events:
        notify_date = string_to_datetime(row['notify_date'] if row['notify_date'] != '' else row['begin_date'])
        if now >= notify_date >= do_not_notify_border and row.get('is_notify_flag', 0) == 0:
            if row['notify_flag'] == '1':
                events_handler_auto(row)
            if row['notify_flag'] == '0':
                events_handler_manual(row)


scheduler.start()
scheduler.add_job(func=reminder, trigger='interval', minutes=config.scheduler_interval_min)
