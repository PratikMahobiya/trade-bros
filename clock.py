from tasks import PivotUpdate, BasicSetupJob, DeleteLogs, FyersSetup, NotifyUsers, CallPutAction, RecordUpdate, StayAwake, Minute1, Daily_P_L_Update
from apscheduler.schedulers.background import BackgroundScheduler
import tzlocal

""" 
    to run from console
    from tasks import BasicSetupJob as bs, FyersSetup as fy, DeleteLogs as dl
    fy()
    bs()
    dl()
"""
def start():
    sched = BackgroundScheduler(timezone=str(tzlocal.get_localzone()))
    FyersSetup()

    # Schedules job_function to be run on the Monday to Friday
    sched.add_job(Daily_P_L_Update, 'cron', day_of_week='mon-fri',
                hour='9-15', second='*/5', timezone='Asia/Kolkata')
    sched.add_job(FyersSetup, 'cron', day_of_week='mon-fri',
                hour='9-15', minute='*/5', timezone='Asia/Kolkata')
    sched.add_job(StayAwake, 'cron', day_of_week='mon-fri',
                hour='9-15', second='*/40', timezone='Asia/Kolkata')
    sched.add_job(DeleteLogs, 'cron', day_of_week='mon-fri',
                hour='9', minute='17', second='30', timezone='Asia/Kolkata')
    sched.add_job(NotifyUsers, 'cron', day_of_week='mon-fri',
                hour='15', minute='19', timezone='Asia/Kolkata')
    sched.add_job(PivotUpdate, 'cron', day_of_week='mon-fri',
                hour='9', minute='17', timezone='Asia/Kolkata')
    sched.add_job(RecordUpdate, 'cron', day_of_week='mon-fri',
                hour='15', minute='18', timezone='Asia/Kolkata')
    sched.add_job(BasicSetupJob, 'cron', day_of_week='mon-fri',
                hour='15', minute='35', timezone='Asia/Kolkata')
    sched.add_job(CallPutAction, 'cron', day_of_week='mon-fri',
                hour='9-15', second='*/5', timezone='Asia/Kolkata')
    sched.add_job(Minute1, 'cron', day_of_week='mon-fri',
                hour='9-15', minute='*/1', timezone='Asia/Kolkata')
    sched.start()
    return True
