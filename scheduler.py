
from apscheduler.schedulers.blocking import BlockingScheduler
from app import rodar

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=30)
def job():
    print("Executando coleta...")
    rodar()

sched.start()