import tzlocal
from django.contrib.auth.models import User
from task import BrokerConnection, stay_awake, SymbolSetup, Equity_BreakOut_1, FnO_BreakOut_1
from apscheduler.schedulers.background import BackgroundScheduler


def start():
    sched = BackgroundScheduler(timezone=str(tzlocal.get_localzone()), daemon=True)
    if not User.objects.filter(username='TradeBros').exists():
        User.objects.create_superuser(
            username='TradeBros',
            password='admin'
        )
        print('Superuser has been created.')

    # Schedules job_function to be run on the Monday to Friday
    sched.add_job(stay_awake, 'cron', day_of_week='mon-fri',
                second='*/40', timezone='Asia/Kolkata')
    sched.add_job(SymbolSetup, 'cron', day_of_week='mon-fri',
                hour='8', minute='45', timezone='Asia/Kolkata')
    sched.add_job(BrokerConnection, 'cron', day_of_week='mon-fri',
                hour='9', minute='5', timezone='Asia/Kolkata')
    sched.add_job(Equity_BreakOut_1, 'cron', day_of_week='mon-fri',
                hour='9-15', minute='*/5', timezone='Asia/Kolkata')
    sched.add_job(FnO_BreakOut_1, 'cron', day_of_week='mon-fri',
                hour='9-15', minute='*/5', timezone='Asia/Kolkata')
    sched.start()
    return True
