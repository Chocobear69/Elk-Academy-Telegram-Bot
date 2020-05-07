import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler

from elk_bot_gsheets_handler import *
from elk_bot_db_handler import DataBaseHandler
from logger import get_simple_logger

######################################################################################
telebot.apihelper.proxy = {'https': 'socks5://{}:{}'.format(config.ip, config.port)}
######################################################################################
scheduler = BackgroundScheduler()
db_handler = DataBaseHandler()
gsheets = GoogleSheetsHandler()
logger = get_simple_logger('elk_bot')
bot = telebot.TeleBot(config.token)
######################################################################################
admins = gsheets.get_admins()
######################################################################################


@bot.message_handler(commands=['start'])
def init(message):
    if message.chat.id < 0 and message.from_user.id in admins:
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id, 'Как назовем группу?', reply_markup=markup)
        bot.register_for_reply(msg, add_group, user_id=message.from_user.id)
    elif message.chat.id > 0:
        bot.send_message(message.chat.id, config.first_message)


def add_group(message, user_id):
    if message.from_user.id == user_id and message.content_type == 'text':
        try:
            gsheets.set_group(message.text, message.chat.id)
            bot.reply_to(message, 'Done')
        except Exception as e:
            bot.reply_to(message, 'Something goes wrong(')
            logger.warning('ELK-BOT-SET-GROUP: \n' + str(e))


@bot.message_handler(commands=['id'])
def send_id(message):
    bot.reply_to(message, message.chat.id)


@bot.message_handler(commands=['alert'])
def send_custom_message(message):
    if message.from_user.id in admins:
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id, 'Что передать?', reply_markup=markup)
        bot.register_for_reply(msg, reply_message_handler, user_id=message.from_user.id)


def reply_message_handler(message, user_id):
    if message.from_user.id == user_id and message.content_type == 'text':
        groups = gsheets.get_group_list()
        for group in groups:
            bot.send_message(group, message.text)
    else:
        bot.reply_to(message, 'Не-не-не, что-то не так')


def messages_handler():
    """Update admins"""
    global admins
    admins = gsheets.get_admins()
    """"Message handler"""
    notify = {
        datetime(1970, 1, 1, 0, 0): dict()
    }
    try:
        messages = gsheets.get_prepared_messages()
        if messages:
            groups = gsheets.get_group_list()
            for message_id, message in messages.items():
                notify[message] = []
                db_id = db_handler.write_message(message, datetime.now())
                notify[datetime(1970, 1, 1, 0, 0)][message] = db_id

                for group_id, group_name in groups.items():
                    bot.send_message(group_id, message)
                    notify[message].append(group_name)
                    gsheets.delete_event(message_id)
                    logger.info('ELK-BOT-SENDING-MESSAGE: \n' + 'MESSAGE: \n' + message)
    except Exception as e:
        logger.warning('ELK-BOT: WHILE SENDING MESSAGE NEXT ERROR OCCUR \n' + str(e))
        notify['error: Что-то пошло не так, обратитесь к администратору.'] = ['Info_chat']
    finally:
        if notify:
            notify_admins(notify)


def notify_admins(notify_dict):
    id_dict = notify_dict.pop(datetime(1970, 1, 1, 0, 0))

    for message, groups_list in notify_dict.items():
        trimmed_message = message[0:60] + '...'
        groups = ',\n'.join(groups_list)
        bot.send_message(config.info_chat_id, config.info_message_template.format(message_id=id_dict[message],
                                                                                  message=trimmed_message,
                                                                                  groups=groups))


@bot.message_handler(commands=['get_message'])
def get_message(message):
    markup = types.ForceReply(selective=False)
    msg = bot.send_message(message.chat.id, 'id?', reply_markup=markup)
    bot.register_for_reply(msg, get_message_by_id, user_id=message.from_user.id)


def get_message_by_id(message, user_id):
    if message.from_user.id == user_id and message.content_type == 'text':
        bot.reply_to(message, db_handler.get_message_by_id(message.text))


@bot.message_handler(commands=['add_admin'])
def set_admin(message):
    if message.from_user.id in config.sup_user_id:
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id, 'id?', reply_markup=markup)
        bot.register_for_reply(msg, set_admin_by_id, user_id=message.from_user.id)


def set_admin_by_id(message, user_id):
    if message.from_user.id == user_id and message.content_type == 'text':
        adm_id, name = message.text.split(',')
        gsheets.set_admin(name, adm_id)


@bot.message_handler(func=lambda message: message.from_user.id not in admins)
def count_messages(message):
    pass


def main():
    scheduler.start()
    scheduler.add_job(func=messages_handler, trigger='interval', minutes=config.scheduler_interval_min)

    while True:
        try:
            bot.infinity_polling(True)
            break
        except Exception as e:
            bot.stop_polling()
            logger.warning('ELK-BOT-POLLING:\n' + str(e))


if __name__ == '__main__':
    main()


