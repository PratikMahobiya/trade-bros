import tzlocal
from task import BrokerConnection, socket_setup, stay_awake
from apscheduler.schedulers.background import BackgroundScheduler


def start():
    sched = BackgroundScheduler(timezone=str(tzlocal.get_localzone()), daemon=True)

    socket_setup()

    # Schedules job_function to be run on the Monday to Friday
    sched.add_job(stay_awake, 'cron', day_of_week='mon-fri',
                second='*/40', timezone='Asia/Kolkata')
    sched.add_job(BrokerConnection, 'cron', day_of_week='mon-fri',
                hour='9', minute='10', timezone='Asia/Kolkata')
    sched.add_job(socket_setup, 'cron', day_of_week='mon-fri',
                hour='9-15', minute='*/30', timezone='Asia/Kolkata')
    sched.start()
    return True
