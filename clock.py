import tzlocal
from django.contrib.auth.models import User
from apscheduler.schedulers.background import BackgroundScheduler
from task import AccountConnection, BrokerConnection, CheckFnOSymbolDisable, CheckTodayEntry, MarketDataUpdate, PivotUpdate, SquareOff, stay_awake, SymbolSetup, Equity_BreakOut_1, FnO_BreakOut_1, NotifyUsers, StopSocketSetup, SocketSetup, CheckLtp, TriggerBuild


def start():
    sched = BackgroundScheduler(timezone=str(tzlocal.get_localzone()), daemon=True)
    if not User.objects.filter(username='Master').exists():
        User.objects.create_superuser(
            username='Master',
            password='admin'
        )
        print('Superuser has been created.')
    if not User.objects.filter(username='MoneyBall').exists():
        User.objects.create_user(
            username='MoneyBall',
            password='admin'
        )
        print('Staff User has been created.')
    if not User.objects.filter(username='User').exists():
        User.objects.create_user(
            username='User',
            password='user'
        )
        print('User has been created.')

    AccountConnection()

    # Schedules job_function to be run on the Monday to Friday
    sched.add_job(stay_awake, 'cron',
                minute='*/2', timezone='Asia/Kolkata')
    sched.add_job(BrokerConnection, 'cron',
                hour='9', minute='0', timezone='Asia/Kolkata')
    sched.add_job(SymbolSetup, 'cron',
                hour='9', minute='2', timezone='Asia/Kolkata')
    sched.add_job(AccountConnection, 'cron',
                hour='9', minute='10', timezone='Asia/Kolkata')
    sched.add_job(PivotUpdate, 'cron',
                hour='9', minute='16', timezone='Asia/Kolkata')
    sched.add_job(NotifyUsers, 'cron',
                hour='20', minute='0', timezone='Asia/Kolkata')
    sched.add_job(MarketDataUpdate, 'cron', day_of_week='mon-fri',
                hour='8-15', minute='*/13', timezone='Asia/Kolkata')
    sched.add_job(CheckTodayEntry, 'cron', day_of_week='mon-fri',
                hour='15', minute='20', timezone='Asia/Kolkata')
    sched.add_job(CheckFnOSymbolDisable, 'cron', day_of_week='mon-fri',
                hour='9-15', minute='*/3', timezone='Asia/Kolkata')
    sched.add_job(SquareOff, 'cron', day_of_week='mon-fri',
                hour='15', minute='17', timezone='Asia/Kolkata')
    sched.add_job(Equity_BreakOut_1, 'cron', day_of_week='mon-fri',
                hour='9-15', minute='*/2', timezone='Asia/Kolkata')
    sched.add_job(FnO_BreakOut_1, 'cron', day_of_week='mon-fri',
                hour='9-15', minute='*/5', timezone='Asia/Kolkata')
    sched.add_job(TriggerBuild, 'cron',
                hour='8,12,16,20,0,4', minute='55', timezone='Asia/Kolkata')
    sched.add_job(SocketSetup, 'cron',
                hour='9', minute='12', timezone='Asia/Kolkata')
    sched.add_job(CheckLtp, 'cron', day_of_week='mon-fri', max_instances=2,
                hour='9-15', second='*/30', timezone='Asia/Kolkata')
    # sched.add_job(StopSocketSetup, 'cron', day_of_week='mon-fri',
    #             hour='5', minute='5', timezone='Asia/Kolkata')
    sched.start()
    SocketSetup(log_identifier='Restart')
    return True
