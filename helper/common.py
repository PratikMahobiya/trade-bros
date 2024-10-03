import requests
import calendar
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta
from django.utils.html import format_html

def colour(value):
    if value == 0:
        return value
    elif value < 0:
        return format_html('<strong style="color:Red;">{}</strong>', value)
    return format_html('<strong style="color:Green;">{}</strong>', value)


def calculate_volatility(dt):
    dt['Return'] = 100 * (dt['Close'].pct_change())
    daily_volatility = dt['Return'].std()
    return daily_volatility


def up_model(obj, price):
    diff = price - obj.price
    profit = round(((diff/obj.price) * 100), 2)
    # if obj.mode == 'CE':
    if profit < 0:
      return format_html('<strong style="color:Red;">{}</strong>', profit)
    return format_html('<strong style="color:Green;">{}</strong>', profit)
    # else:
    #   if profit > 0:
    #     return format_html('<strong style="color:Red;">{}</strong>', -profit)
    #   return format_html('<strong style="color:Green;">{}</strong>', -profit)


def last_thursday(now):
    # Get the last day of the month
    last_day = calendar.monthrange(now.date().year, now.date().month)[1]
    
    # Create a date object for the last day of the month
    last_date = datetime(now.date().year, now.date().month, last_day)
    
    # Find the last Thursday
    while last_date.weekday() != calendar.THURSDAY:
        last_date -= timedelta(days=1)
        
    return last_date


def get_nifty50():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    }

    s = requests.get("https://nsearchives.nseindia.com/content/indices/ind_nifty50list.csv", headers=headers)

    # Decode the byte string
    decoded_data = s.content.decode('utf-8')

    # Use StringIO to create a file-like object from the string
    data_io = StringIO(decoded_data)

    # Read the CSV data into a DataFrame
    df = pd.read_csv(data_io)
    return list(df['Symbol'])


def get_nifty100():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    }

    s = requests.get("https://nsearchives.nseindia.com/content/indices/ind_nifty100list.csv", headers=headers)

    # Decode the byte string
    decoded_data = s.content.decode('utf-8')

    # Use StringIO to create a file-like object from the string
    data_io = StringIO(decoded_data)

    # Read the CSV data into a DataFrame
    df = pd.read_csv(data_io)
    return list(df['Symbol'])


def get_nifty200():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    }

    s = requests.get("https://nsearchives.nseindia.com/content/indices/ind_nifty200list.csv", headers=headers)

    # Decode the byte string
    decoded_data = s.content.decode('utf-8')

    # Use StringIO to create a file-like object from the string
    data_io = StringIO(decoded_data)

    # Read the CSV data into a DataFrame
    df = pd.read_csv(data_io)
    return list(df['Symbol'])


def get_midcpnifty50():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    }

    s = requests.get("https://nsearchives.nseindia.com/content/indices/ind_niftymidcap50list.csv", headers=headers)

    # Decode the byte string
    decoded_data = s.content.decode('utf-8')

    # Use StringIO to create a file-like object from the string
    data_io = StringIO(decoded_data)

    # Read the CSV data into a DataFrame
    df = pd.read_csv(data_io)
    return list(df['Symbol'])


def get_midcpnifty100():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    }

    s = requests.get("https://nsearchives.nseindia.com/content/indices/ind_niftymidcap100list.csv", headers=headers)

    # Decode the byte string
    decoded_data = s.content.decode('utf-8')

    # Use StringIO to create a file-like object from the string
    data_io = StringIO(decoded_data)

    # Read the CSV data into a DataFrame
    df = pd.read_csv(data_io)
    return list(df['Symbol'])


def get_midcpnifty150():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    }

    s = requests.get("https://nsearchives.nseindia.com/content/indices/ind_niftymidcap150list.csv", headers=headers)

    # Decode the byte string
    decoded_data = s.content.decode('utf-8')

    # Use StringIO to create a file-like object from the string
    data_io = StringIO(decoded_data)

    # Read the CSV data into a DataFrame
    df = pd.read_csv(data_io)
    return list(df['Symbol'])


def get_smallcpnifty50():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    }

    s = requests.get("https://nsearchives.nseindia.com/content/indices/ind_niftysmallcap_50list.csv", headers=headers)

    # Decode the byte string
    decoded_data = s.content.decode('utf-8')

    # Use StringIO to create a file-like object from the string
    data_io = StringIO(decoded_data)

    # Read the CSV data into a DataFrame
    df = pd.read_csv(data_io)
    return list(df['Symbol'])


def get_smallcpnifty100():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    }

    s = requests.get("https://nsearchives.nseindia.com/content/indices/ind_niftysmallcap100list.csv", headers=headers)

    # Decode the byte string
    decoded_data = s.content.decode('utf-8')

    # Use StringIO to create a file-like object from the string
    data_io = StringIO(decoded_data)

    # Read the CSV data into a DataFrame
    df = pd.read_csv(data_io)
    return list(df['Symbol'])


def get_smallcpnifty250():
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        'Sec-Fetch-User': '?1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
    }

    s = requests.get("https://nsearchives.nseindia.com/content/indices/ind_niftysmallcap250list.csv", headers=headers)

    # Decode the byte string
    decoded_data = s.content.decode('utf-8')

    # Use StringIO to create a file-like object from the string
    data_io = StringIO(decoded_data)

    # Read the CSV data into a DataFrame
    df = pd.read_csv(data_io)
    return list(df['Symbol'])
