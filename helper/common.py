from datetime import timedelta
from helper.indicator import SUPER_TREND
from django.utils.html import format_html

def calculate_volatility(dt):
  dt['Return'] = 100 * (dt['Close'].pct_change())
  daily_volatility = dt['Return'].std()
  return round(daily_volatility,4)


def next_expiry_date(date, weekday):
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return date + timedelta(days_ahead)



def colour(value):
    if value == 0:
        return value
    elif value < 0:
        return format_html('<strong style="color:Red;">{}</strong>', value)
    return format_html('<strong style="color:Green;">{}</strong>', value)


def Entry_Call(data_frame, index_obj):
  super_trend = SUPER_TREND(high=data_frame['High'], low=data_frame['Low'], close=data_frame['Close'], length=10, multiplier=3)
  if data_frame['Low'].iloc[-1] > super_trend[-1] and data_frame['Close'].iloc[-2] < super_trend[-2]:
    if (data_frame['High'].iloc[-1] > index_obj.r1 and data_frame['Low'].iloc[-1] < index_obj.r1) or (data_frame['High'].iloc[-1] > index_obj.r2 and data_frame['Low'].iloc[-1] < index_obj.r2) or (data_frame['High'].iloc[-1] > index_obj.pivot and data_frame['Low'].iloc[-1] < index_obj.pivot):
      return False
    return True
  return False


def Entry_Put(data_frame, index_obj):
  super_trend = SUPER_TREND(high=data_frame['High'], low=data_frame['Low'], close=data_frame['Close'], length=10, multiplier=3)
  if data_frame['High'].iloc[-1] < super_trend[-1] and data_frame['Close'].iloc[-2] > super_trend[-2]:
    if (data_frame['High'].iloc[-1] > index_obj.s1 and data_frame['Low'].iloc[-1] < index_obj.s1) or (data_frame['High'].iloc[-1] > index_obj.s2 and data_frame['Low'].iloc[-1] < index_obj.s2) or (data_frame['High'].iloc[-1] > index_obj.pivot and data_frame['Low'].iloc[-1] < index_obj.pivot):
      return False
    return True
  return False