from telegram.ext import Updater, CommandHandler
from telegram_features.telegram_private_keys import telegram_api_key,tel_id
from telegram_features.telegram_notification import send_notification
from main import init_trader
from functools import wraps

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != tel_id:
            send_notification('Unauthorized access denied for {}.'.format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped


@restricted
def activate_trader_bot(bot, update, job_queue, user_data):
    trader_job = job_queue.run_repeating(init_trader, interval=90, first=0)
    user_data['trader_job'] = trader_job
    send_notification('торговый бот начал работу')


@restricted
def deactivate_trader_bot(bot, update, user_data):
    trader_job = user_data.get('trader_job')
    if trader_job:
        trader_job.schedule_removal()
        send_notification('торговый бот завершил работу')
    else:
        send_notification('торговый бот не завершил работу')

def main():
    updater = Updater(telegram_api_key)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("activate", activate_trader_bot, pass_job_queue=True, pass_user_data=True))
    dp.add_handler(CommandHandler("deactivate", deactivate_trader_bot, pass_user_data=True))
    updater.start_polling(timeout=500)

if __name__ == '__main__':
    main()
