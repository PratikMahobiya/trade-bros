import tzlocal
from task import BrokerConnection, socket_setup, stay_awake
from apscheduler.schedulers.background import BackgroundScheduler


def start():
    sched = BackgroundScheduler(timezone=str(tzlocal.get_localzone()), daemon=True)

    socket_setup(log_identifier='Restart')

    # Schedules job_function to be run on the Monday to Friday
    sched.add_job(stay_awake, 'cron',
                second='*/40', timezone='Asia/Kolkata')
    sched.add_job(BrokerConnection, 'cron',
                hour='8', minute='55', timezone='Asia/Kolkata')
    sched.add_job(socket_setup, 'cron',
                hour='9', minute='10', timezone='Asia/Kolkata')
    sched.start()
    return True
