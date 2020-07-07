import re
import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler

from elk_bot_gsheets_handler import *
from elk_bot_db_handler import DataBaseHandler
from logger import get_simple_logger

scheduler = BackgroundScheduler()
db_handler = DataBaseHandler()
gsheets = GoogleSheetsHandler()
logger = get_simple_logger('elk_bot')
bot = telebot.TeleBot(config.token)
######################################################################################
admins = gsheets.get_admins()
groups = gsheets.get_groups()
######################################################################################


@bot.message_handler(commands=['start'])
def init(message):
    if message.chat.id < 0 and message.from_user.id in admins:
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id, 'What is this group tag?', reply_markup=markup)
        bot.register_for_reply(msg, add_group, user_id=message.from_user.id, chat_id=message.chat.id)
        bot.send_message(message.chat.id, config.first_message)


def add_group(message, user_id, chat_id):
    if message.chat.id == chat_id and message.from_user.id == user_id and message.content_type == 'text':
        try:
            gsheets.set_group(message.text, message.chat.id)
            db_handler.set_group(message)
            bot.reply_to(message, 'Done')
        except Exception as e:
            bot.reply_to(message, 'Something goes wrong(')
            logger.warning('While adding group next Exception occur: \n' + str(e))


@bot.message_handler(commands=['hello'])
def set_customer(message):
    if message.from_user.id not in admins and message.chat.id in groups:
        status = db_handler.set_customer(message)
        if status:
            bot.reply_to(message, 'Hello, darling!')
        else:
            bot.reply_to(message, 'I know who you are)')
    else:
        bot.reply_to(message, 'I know who you are)')


@bot.message_handler(commands=['id'])
def send_id(message):
    bot.reply_to(message, 'Your id is: ' + str(message.from_user.id))


@bot.message_handler(commands=['add_admin'])
def set_admin(message):
    if message.from_user.id in config.sup_user_id and message.chat.id > 0:
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id, 'New admin id plz?', reply_markup=markup)
        bot.register_for_reply(msg, set_admin_by_id, user_id=message.from_user.id)


def set_admin_by_id(message, user_id):
    if message.from_user.id == user_id and message.content_type == 'text':
        adm_id, name = message.text.split(',')
        gsheets.set_admin(name, adm_id)


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
        if lower_text.startswith('n'):
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
    groups = gsheets.get_groups()
    admins = gsheets.get_admins()



def main():
    scheduler.start()
    scheduler.add_job(func=update_admins_groups, trigger='interval', minutes=config.scheduler_interval_min)

    while True:
        try:
            bot.infinity_polling(True)
            break
        except Exception as e:
            bot.stop_polling()
            logger.warning('ELK-BOT-POLLING:\n' + str(e))


if __name__ == '__main__':
    main()


