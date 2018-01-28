from telegram import Bot
from telegram_features.telegram_keys import tel_id, telegram_api_key

bot = Bot(telegram_api_key)


def send_notification(text):
    bot.send_message(tel_id, text)
