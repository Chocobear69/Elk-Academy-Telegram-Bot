import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler
from elk_bot_gsheets_handler import *

telebot.apihelper.proxy = {'https': 'socks5://{}:{}'.format(config.ip, config.port)}
scheduler = BackgroundScheduler()
gsheets = GoogleSheetsHandler()
bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def init(message):
    gsheets.set_group('new_group', message.chat.id)


@bot.message_handler(commands=['alert'])
def send_custom_message(message):
    markup = types.ForceReply(selective=False)
    msg = bot.send_message(message.chat.id, 'Что передать?', reply_markup=markup)
    bot.register_for_reply(msg, reply_message_handler, user_id=message.from_user.id)


def reply_message_handler(message, user_id):
    if message.from_user.id == user_id and message.content_type == 'text':
        chat_list = gsheets.get_chat_list()
        for chat in chat_list:
            bot.send_message(chat, message.text)
    else:
        bot.reply_to(message, 'Не-не-не, что-то не так')


def messages_handler():
    messages = gsheets.get_prepared_messages()
    chat_list = gsheets.get_chat_list()
    for message, message_id in messages.items():
        for chat in chat_list:
            bot.send_message(chat, message)
            gsheets.delete_event(message_id)


def main():
    scheduler.start()
    scheduler.add_job(func=messages_handler, trigger='interval', minutes=config.scheduler_interval_min)

    while True:
        try:
            bot.infinity_polling(True)
            break
        except Exception as e:
            bot.stop_polling()


if __name__ == '__main__':
    main()


