import re
import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler

from elk_bot_gsheets_handler import *
from elk_bot_db_handler import DataBaseHandler
import logger

scheduler = BackgroundScheduler()
db_handler = DataBaseHandler()
bot = telebot.TeleBot(config.token)
######################################################################################
admins = db_handler.get_admins()
groups = db_handler.get_groups()
######################################################################################


@bot.message_handler(commands=['start'])
def init(message):
    if message.chat.id < 0 and message.from_user.id in admins:
        bot.send_message(message.chat.id, config.first_message)
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id, 'What is this group tag?', reply_markup=markup)
        bot.register_for_reply(msg, add_group, user_id=message.from_user.id, chat_id=message.chat.id)


def add_group(message, user_id, chat_id):
    if message.chat.id == chat_id and message.from_user.id == user_id and message.content_type == 'text':
        try:
            db_handler.set_group(message)
            bot.reply_to(message, 'Done')
        except Exception as e:
            bot.reply_to(message, 'Something goes wrong(')
            logger.get_logger().error('While adding group next Exception occur: \n' + str(e))


@bot.message_handler(commands=['hello'])
def set_customer(message):
    if message.from_user.id not in admins and message.chat.id in groups:
        status = db_handler.set_customer(message)
        if status:
            bot.reply_to(message, 'Hello, darling!')
        else:
            bot.reply_to(message, 'I know who you are)')


@bot.message_handler(commands=['id'])
def send_id(message):
    bot.reply_to(message, 'Chat id is: ' + str(message.chat.id))


@bot.message_handler(commands=['add_admin'])
def set_admin(message):
    if message.from_user.id in config.sup_user_id and message.chat.id > 0:
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id, 'Enter name and id separated by comma\nExmpl:Admin,391416028',
                               reply_markup=markup)
        bot.register_for_reply(msg, set_admin_by_id, user_id=message.from_user.id)


def set_admin_by_id(message, user_id):
    if message.from_user.id == user_id and message.content_type == 'text':
        name, admin_id = message.text.split(',')
        db_handler.set_admin(name, admin_id)


@bot.message_handler(['remove'])
def del_group(message):
    if message.from_user.id in admins and message.chat.id in groups:
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id, 'Are you sure?(Y/N)', reply_markup=markup)
        bot.register_for_reply(msg, del_group_by_id, user_id=message.from_user.id, group_id=message.chat.id)


def del_group_by_id(message, user_id, group_id):
    if message.from_user.id == user_id and message.chat.id == group_id and message.content_type == 'text':
        lower_text = message.text.lower()
        if lower_text.startswith('y'):
            db_handler.delete_group(message.chat.id)
            bot.reply_to(message, 'Bye ;)')
            bot.leave_chat(message.chat.id)
        elif lower_text.startswith('n'):
            bot.reply_to(message, 'OK!')
        else:
            bot.reply_to(message, 'Try one more time, I believe in you!')


@bot.message_handler(func=lambda msg: msg.from_user.id not in admins and msg.chat.id in groups)
def count_messages(message):
    if message.content_type == 'text':
        if re.findall('.*#{tag}.*'.format(tag=groups[message.chat.id]), message.text):
            db_handler.write_message(message)


def update_admins_groups():
    global admins
    global groups
    groups = db_handler.get_groups()
    admins = db_handler.get_admins()


def check_messages_to_send():
    messages_to_send = db_handler.get_messages_to_send()
    for i in messages_to_send:
        try:
            bot.send_message(i.group_id, i.message_body)
            db_handler.delete_message_to_send(i.message_id)
        except Exception as e:
            logger.get_logger().error(str(e))


def main():
    scheduler.start()
    scheduler.add_job(func=update_admins_groups, trigger='interval', minutes=config.scheduler_interval_min)
    scheduler.add_job(func=check_messages_to_send, trigger='interval', minutes=config.scheduler_interval_min + 1)

    while True:
        try:
            bot.infinity_polling(True)
            break
        except Exception as e:
            bot.stop_polling()
            logger.get_logger().error(str(e))


if __name__ == '__main__':
    main()


