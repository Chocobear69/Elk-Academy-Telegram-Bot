import telebot
from telebot import apihelper
from config import config

apihelper.proxy = {'https': 'socks5://{}:{}'.format(config.ip, config.port)}
bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def init(message):
    bot.reply_to(message, 'Hello, Bro!')


def main():
    while True:
        try:
            bot.infinity_polling(True)
            break
        except Exception:
            bot.stop_polling()


if __name__ == '__main__':
    main()
