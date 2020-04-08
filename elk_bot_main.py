import telebot
from apscheduler.schedulers.background import BackgroundScheduler
#from config import config
from elk_bot_service_provider import ServiceProvider
from elk_bot_gsheets_handler import *

telebot.apihelper.proxy = {'https': 'socks5://{}:{}'.format(config.ip, config.port)}
scheduler = BackgroundScheduler()
bot = telebot.TeleBot(config.token)
services = ServiceProvider()


@bot.message_handler(commands=['start'])
def init(message):
    set_group('new_group', message.chat.id)


def messages_handler():
    messages = get_prepared_messages()
    chat_list = get_chat_list()
    for message in messages:
        for chat in chat_list:
            bot.send_message(chat, message['message_text'])


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


