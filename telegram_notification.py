from telegram import Bot
from main_settings import tel_id

bot = Bot('475039573:AAHYgEqsqBRShxfpImQpYL5z5fx8_xkMi4o')

def send_notification(text):
    bot.send_message(tel_id, text)