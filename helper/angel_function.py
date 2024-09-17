import pytz
import pandas as pd
from datetime import datetime
from trade.settings import broker_connection

def historical_data(token, exchange, now, from_day, interval):
    historicParam = {
        "exchange": exchange,
        "symboltoken": token,
        "interval": interval,
        "fromdate": from_day.strftime("%Y-%m-%d %H:%M"),
        "todate": now.strftime("%Y-%m-%d %H:%M")
    }
    global broker_connection
    data = pd.DataFrame(broker_connection.getCandleData(historicParam)['data'])
    data.rename(columns={
        0: 'date', 1: 'Open', 2: 'High', 3: 'Low', 4: 'Close', 5: 'Volume'}, inplace=True)
    data.index.names = ['date']
    data_frame = data
    # Convert str timestamps to IST
    ist_timezone = pytz.timezone('Asia/Kolkata')
    data_frame['date'] = data_frame['date'].apply(lambda x: datetime.fromisoformat(x).astimezone(ist_timezone))

    # # Compare the minutes
    # if (data_frame['date'].iloc[-1].minute == now.minute) and (data_frame['date'].iloc[-1].hour == now.hour):
    #     data_frame = data_frame.iloc[:-1]
    # elif (data_frame['date'].iloc[-1].date() != now.date()) and interval == '1':
    #     data_frame = data_frame.iloc[:-1]
    # else:
    #     data_frame = data_frame

    data_frame = data_frame.fillna(data_frame.mean())
    return data_frame
