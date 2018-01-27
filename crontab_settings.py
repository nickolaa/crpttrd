from crontab import CronTab

empty_cron = CronTab()
my_user_cron = CronTab(user=True)
users_cron = CronTab(user='username')

./cron
