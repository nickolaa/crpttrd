from crontab import CronTab

# empty_cron = CronTab()
# my_user_cron = CronTab(user=True)
# users_cron = CronTab(user='username')

# ./cron

file_cron = CronTab(tabfile='my_cron.tab')

file_cron.minute.every(5)

start = file_cron.enable()
stop = file_cron.enable(False)
