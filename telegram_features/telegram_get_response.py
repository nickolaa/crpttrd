from telegram.ext import Updater, CommandHandler
from telegram_features.telegram_keys import telegram_api_key
from cron_param.crontab_settings import start, stop

def start_bot(bot, update):
    text = 'Вызван /start'
    start
    update.message.reply_text(text)

def stop_bot(bot, update):
    text = 'Вызван /stop'
    stop
    update.message.reply_text(text)

def main():
    updater = Updater(telegram_api_key)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start_bot))
    dp.add_handler(CommandHandler("start", stop_bot))
