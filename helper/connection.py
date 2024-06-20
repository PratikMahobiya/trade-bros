import os
from SmartApi import SmartConnect
from fyers_apiv3 import fyersModel
import pyotp
from logs.logger import write_error_log

from option.models import Keys
from time import sleep


def AngelOne(username, logger=None):
    conn = None
    broker_obj = None
    try:
        broker_obj = Keys.objects.get(
            broker_name='AngelOne', username=username, is_active=True)
        try:
            global angel_pratik_conn
            angel_pratik_conn.terminateSession(broker_obj.user_id)
        except Exception as e:
            if logger:
                write_error_log(logger, f'Trying to Terminate Angel Session Error: {e}')
        sleep(2)
        conn = SmartConnect(api_key=broker_obj.api_key)
        conn.generateSession(broker_obj.user_id, broker_obj.user_pin, totp=pyotp.TOTP(broker_obj.access_token).now())
    except Exception as e:
        conn = None
        if logger:
            write_error_log(logger, f'AngelOne Connection Error: {e}')
    return conn, broker_obj


def Fyers(username):
    broker_obj = Keys.objects.get(
        broker_name='Fyers', username=username, is_active=True)
    app_id = broker_obj.api_key
    access_token = broker_obj.access_token
    return fyersModel.FyersModel(client_id=app_id, token=access_token)