from datetime import datetime
import pytz

import pandas as pd
from logs.logger import write_error_log, write_info_log


def angel_get_data(token, now, from_day, interval, conn, logger=None):
    try:
        historicParam = {
            "exchange": "NFO",
            "symboltoken": token,
            "interval": interval,
            "fromdate": from_day.strftime("%Y-%m-%d %H:%M"),
            "todate": now.strftime("%Y-%m-%d %H:%M")
        }
        data = pd.DataFrame(conn.getCandleData(historicParam)['data'])
        data.rename(columns={
            0: 'date', 1: 'Open', 2: 'High', 3: 'Low', 4: 'Close', 5: 'Volume'}, inplace=True)
        data.index.names = ['date']
        data_frame = data
        # Convert str timestamps to IST
        ist_timezone = pytz.timezone('Asia/Kolkata')
        data_frame['date'] = data_frame['date'].apply(lambda x: datetime.fromisoformat(x).astimezone(ist_timezone))

        # Compare the minutes
        if (data_frame['date'].iloc[-1].minute == now.minute) and (data_frame['date'].iloc[-1].hour == now.hour):
            # write_info_log(logger, f"SAME_MINUTE: {data_frame['date'].iloc[-1]}: {data_frame['date'].iloc[-1].minute}, {now.minute}, {data_frame['date'].iloc[-1].hour}, {now.hour}")
            data_frame = data_frame.iloc[:-1]
        elif (data_frame['date'].iloc[-1].date() != now.date()) and interval == '1':
            # write_info_log(logger, f"NE_DATE: {data_frame['date'].iloc[-1]}: {data_frame['date'].iloc[-1].date()}, {now.date()}")
            data_frame = data_frame.iloc[:-1]
        else:
            data_frame = data_frame

        data_frame = data_frame.fillna(data_frame.mean())
    except Exception as e:
        if logger:
            write_error_log(logger, f'Angel Get Data: {e}')
            write_error_log(logger, f'Angel Get Data: {token} {data}')
        raise Exception("Angel Error")
    return data_frame


def fyers_get_data(symbol, now, from_day, interval, conn, logger=None):
    try:
        data = {
            "symbol": symbol,
            "resolution": interval,
            "date_format": "1",
            "range_from": from_day.date(),
            "range_to": now.date(),
            "cont_flag": "1"
        }
        data = conn.history(data)
        data = pd.DataFrame(data['candles'])
        data[0] = pd.to_datetime(data[0], unit='s')
        data_frame = data.set_index(
            data[0], drop=False, append=False, inplace=False, verify_integrity=False)
        data_frame.rename(columns={0: 'date', 1: 'Open', 2: 'High',
                        3: 'Low', 4: 'Close', 5: 'Volume'}, inplace=True)        
        data_frame.index.names = ['date']

        # Convert epoch timestamps to IST
        ist_timezone = pytz.timezone('Asia/Kolkata')
        data_frame['date'] = data_frame['date'].apply(lambda x: x.tz_localize('UTC').astimezone(ist_timezone))

        # Compare the minutes
        if (data_frame['date'].iloc[-1].minute == now.minute) and (data_frame['date'].iloc[-1].hour == now.hour):
            # write_info_log(logger, f"SAME_MINUTE: {data_frame['date'].iloc[-1]}: {data_frame['date'].iloc[-1].minute}, {now.minute}, {data_frame['date'].iloc[-1].hour}, {now.hour}")
            data_frame = data_frame.iloc[:-1]
        elif (data_frame['date'].iloc[-1].date() != now.date()) and interval == '1':
            # write_info_log(logger, f"NE_DATE: {data_frame['date'].iloc[-1]}: {data_frame['date'].iloc[-1].date()}, {now.date()}")
            data_frame = data_frame.iloc[:-1]
        else:
            data_frame = data_frame

        data_frame = data_frame.fillna(data_frame.mean())
    except Exception as e:
        if logger:
            write_error_log(logger, f'Fyer Get Data: {e}')
            write_error_log(logger, f'Fyer Get Data: {symbol} {data}')
        raise Exception("Fyer Error")
    return data_frame