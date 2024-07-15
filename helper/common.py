from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from helper.indicator import SUPER_TREND
from django.utils.html import format_html

from option.models import Transaction

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
    if (abs(data_frame['Close'].iloc[-1] - data_frame['Open'].iloc[-2]) > index_obj.chain_strike_price_diff) or (data_frame['High'].iloc[-1] > index_obj.r1 and data_frame['Low'].iloc[-1] < index_obj.r1) or (data_frame['High'].iloc[-1] > index_obj.r2 and data_frame['Low'].iloc[-1] < index_obj.r2) or (data_frame['High'].iloc[-1] > index_obj.pivot and data_frame['Low'].iloc[-1] < index_obj.pivot):
      return False
    return True
  return False


def Entry_Put(data_frame, index_obj):
  super_trend = SUPER_TREND(high=data_frame['High'], low=data_frame['Low'], close=data_frame['Close'], length=10, multiplier=3)
  if data_frame['High'].iloc[-1] < super_trend[-1] and data_frame['Close'].iloc[-2] > super_trend[-2]:
    if (abs(data_frame['Open'].iloc[-2] - data_frame['Close'].iloc[-1]) > index_obj.chain_strike_price_diff) or (data_frame['High'].iloc[-1] > index_obj.s1 and data_frame['Low'].iloc[-1] < index_obj.s1) or (data_frame['High'].iloc[-1] > index_obj.s2 and data_frame['Low'].iloc[-1] < index_obj.s2) or (data_frame['High'].iloc[-1] > index_obj.pivot and data_frame['Low'].iloc[-1] < index_obj.pivot):
      return False
    return True
  return False


def Check_Entry(now, configuration_obj, index_obj, days_difference):
  # Check daily Stoploss
  if sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT').values_list('profit', flat=True)) < -configuration_obj.daily_fixed_stoploss:
    return True
  
  # Check expiry index Entry Time
  elif now.time() > time(15, 3, 00) and now.date() == index_obj.expiry_date:
    return True

  # Check expiry index Target
  elif now.date() == index_obj.expiry_date and (sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT', index=index_obj.index).values_list('profit', flat=True)) > index_obj.fixed_target + 5):
    return True

  # Check expiry index Stoploss
  elif now.date() == index_obj.expiry_date and (sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT', index=index_obj.index).values_list('profit', flat=True)) < -(index_obj.stoploss+20)):
    return True

  # Check Thrusday Banknifty index Target 
  elif index_obj.index in ['BANKNIFTY'] and days_difference in [6]:
    if (sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT', index=index_obj.index).values_list('profit', flat=True)) > 23):
      return True
    elif (sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT', index=index_obj.index).values_list('profit', flat=True)) < -index_obj.stoploss):
      return True
    else:
      return False

  # Check Thrusday, Friday Finnifty index Target
  elif index_obj.index in ['FINNIFTY'] and days_difference in [6, 5]:
    if (sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT', index=index_obj.index).values_list('profit', flat=True)) > 15):
      return True
    elif (sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT', index=index_obj.index).values_list('profit', flat=True)) < -index_obj.stoploss):
      return True
    else:
      return False

  # Check non expiry index Target
  elif now.date() != index_obj.expiry_date and (sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT', index=index_obj.index).values_list('profit', flat=True)) > index_obj.fixed_target/(days_difference+1)):
    return True

  # Check non expiry index Stoploss
  elif now.date() != index_obj.expiry_date and (sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT', index=index_obj.index).values_list('profit', flat=True)) < -index_obj.stoploss):
    return True

  # default false
  else:
    return False
