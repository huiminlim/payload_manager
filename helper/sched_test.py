from datetime import datetime
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler


def job(text):
    print(text)


scheduler = BackgroundScheduler()
# In 2020-10-19 00:28:00 Run once job Method
scheduler.add_job(job, 'date', run_date=datetime(
    2020, 10, 19, 0, 28, 0), args=['text2'])
scheduler.start()

while True:
    pass
