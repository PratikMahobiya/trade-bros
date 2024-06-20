from logs.models import Log
from datetime import datetime
from zoneinfo import ZoneInfo


def create_logger(file_name=None):
    """
        create Logs in DB
    """
    get, _ = Log.objects.get_or_create(log_name=file_name)
    return get


def write_info_log(log_file_obj, data_):
    """
        Write Info Logs in DB
    """
    log_file_obj.log_desc = f"{log_file_obj.log_desc}[{datetime.now(tz=ZoneInfo('Asia/Kolkata')).strftime('%d-%b-%Y %H:%M:%S')}] Info: {data_}" + '\n'
    log_file_obj.save()


def write_error_log(log_file_obj, data_):
    """
        Write Error Logs in DB
    """
    log_file_obj.log_desc = f"{log_file_obj.log_desc}[{datetime.now(tz=ZoneInfo('Asia/Kolkata')).strftime('%d-%b-%Y %H:%M:%S')}] Error: {data_}" + '\n'
    log_file_obj.error = True
    log_file_obj.save()


def write_warning_log(log_file_obj, data_):
    """
        Write Warning Logs in DB
    """
    log_file_obj.log_desc = f"{log_file_obj.log_desc}[{datetime.now(tz=ZoneInfo('Asia/Kolkata')).strftime('%d-%b-%Y %H:%M:%S')}] Warning: {data_}" + '\n'
    log_file_obj.save()


def write_critical_log(log_file_obj, data_):
    """
        Write Critical Logs in DB
    """
    log_file_obj.log_desc = f"{log_file_obj.log_desc}[{datetime.now(tz=ZoneInfo('Asia/Kolkata')).strftime('%d-%b-%Y %H:%M:%S')}] Critical: {data_}" + '\n'
    log_file_obj.save()