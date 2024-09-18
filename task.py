import pyotp
import requests
from time import sleep
from zoneinfo import ZoneInfo
from SmartApi import SmartConnect
from stock.models import StockConfig
from datetime import datetime, time, timedelta
from helper.common import calculate_volatility
from helper.angel_function import historical_data
from helper.trade_action import Price_Action_Trade
from system_conf.models import Configuration, Symbol
from trade.settings import BED_URL_DOMAIN, BROKER_API_KEY, BROKER_PIN, BROKER_TOTP_KEY, BROKER_USER_ID, broker_connection


def stay_awake():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'Pratik: Stay Awake: Runtime: {now.strftime("%d-%b-%Y %H:%M:%S")}')
    x = requests.get(f"{BED_URL_DOMAIN}/api/trade/awake", verify=False)
    print(f'Pratik: Stay Awake: Execution Time(hh:mm:ss): {x.status_code} : {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def SymbolSetup():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'Pratik: Symbol Setup: Started')
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    data = requests.get(url).json()
    
    Symbol.objects.filter(expiry__lt=now.date(), is_active=True).delete()

    for i in data:
        product = None
        expity_date = datetime.strptime(i['expiry'], '%d%b%Y') if i['expiry'] else None
        if i['instrumenttype'] in ['OPTSTK'] and (expity_date.month == now.month): # , 'OPTIDX'
            product = 'future'
        # elif i['instrumenttype'] in ['OPTFUT']:
        #     product = 'future'
        elif i['symbol'].endswith('-EQ'):
            product = 'equity'
        if product is not None:
            obj, _ = Symbol.objects.get_or_create(
                product=product,
                name=i['name'],
                symbol=i['symbol']
                )
            obj.token=i['token']
            obj.strike=int(i['strike'].split('.')[0])/100
            obj.exchange=i['exch_seg']
            obj.expiry=expity_date
            obj.lot=int(i['lotsize'])
            obj.save()
    print(f'Pratik: Symbol Setup: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def BrokerConnection():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        print(f'Pratik: Broker Connection: Started')
        global broker_connection
        try:
            broker_connection.terminateSession(BROKER_USER_ID)
        except Exception as e:
            print(f'Pratik: Broker Connection: Trying to Terminate Session Error: {e}')
        
        connection = SmartConnect(api_key=BROKER_API_KEY)
        connection.generateSession(BROKER_USER_ID, BROKER_PIN, totp=pyotp.TOTP(BROKER_TOTP_KEY).now())
        broker_connection = connection
    except Exception as e:
        print(f'Pratik: Broker Connection: Error: {e}')
    print(f'Pratik: Broker Connection: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def Equity_BreakOut_1():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    product = 'equity'
    log_identifier = 'Equity_BreakOut_1'
    print(f'Pratik: {log_identifier}: Runtime : {product} : {now.strftime("%d-%b-%Y %H:%M:%S")}')

    try:
        if now.time() < time(9, 18, 00):
            raise Exception("Entry Not Started")
        elif now.time() > time(15, 14, 00):
            raise Exception("Entry Not Stopped")

        configuration_obj = Configuration.objects.filter(product=product)[0]

        option_enables_symbols = ['NESTLEIND', 'LTTS', 'WIPRO', 'M&MFIN', 'PVRINOX', 'SRF', 'SUNTV', 'TECHM', 'ADANIPORTS', 'TCS', 'BIOCON', 'UPL', 'TATACHEM', 'MFSL', 'GODREJPROP', 'DIVISLAB', 'MOTHERSON', 'VEDL', 'ZYDUSLIFE', 'INDIAMART', 'SYNGENE', 'CUB', 'LT', 'ACC', 'HDFCLIFE', 'DRREDDY', 'NATIONALUM', 'LAURUSLABS', 'MARUTI', 'BANKBARODA', 'HINDCOPPER', 'TATACONSUM', 'ABBOTINDIA', 'DIXON', 'BAJFINANCE', 'ASIANPAINT', 'ESCORTS', 'GUJGASLTD', 'INDUSINDBK', 'AARTIIND', 'BHARTIARTL', 'BANDHANBNK', 'SBIN', 'UBL', 'ASTRAL', 'RELIANCE', 'PETRONET', 'GNFC', 'MANAPPURAM', 'GRANULES', 'UNITDSPR', 'SAIL', 'INDIGO', 'TITAN', 'LTF', 'BAJAJFINSV', 'BHEL', 'DABUR', 'INDUSTOWER', 'ONGC', 'TATASTEEL', 'ABCAPITAL', 'ICICIBANK', 'KOTAKBANK', 'ULTRACEMCO', 'COLPAL', 'COALINDIA', 'OFSS', 'MARICO', 'TORNTPHARM', 'CROMPTON', 'SBILIFE', 'BOSCHLTD', 'RAMCOCEM', 'HINDALCO', 'BHARATFORG', 'BPCL', 'GAIL', 'BERGEPAINT', 'ALKEM', 'SUNPHARMA', 'TRENT', 'IDEA', 'HAL', 'PAGEIND', 'VOLTAS', 'LICHSGFIN', 'RECLTD', 'HDFCBANK', 'JSWSTEEL', 'FEDERALBNK', 'ASHOKLEY', 'IOC', 'COFORGE', 'ABB', 'JINDALSTEL', 'LUPIN', 'TATAPOWER', 'INDHOTEL', 'HCLTECH', 'JUBLFOOD', 'SHREECEM', 'IDFC', 'TATACOMM', 'HEROMOTOCO', 'BALRAMCHIN', 'BAJAJ-AUTO', 'LALPATHLAB', 'SBICARD', 'ITC', 'MPHASIS', 'NMDC', 'APOLLOTYRE', 'LTIM', 'MCX', 'PFC', 'PIIND', 'IGL', 'PNB', 'IEX', 'CONCOR', 'GLENMARK', 'DALBHARAT', 'POLYCAB', 'HINDPETRO', 'NAUKRI', 'HDFCAMC', 'ICICIGI', 'MGL', 'AUROPHARMA', 'PEL', 'PIDILITIND', 'TATAMOTORS', 'CHAMBLFERT', 'AUBANK', 'DEEPAKNTR', 'HINDUNILVR', 'METROPOLIS', 'BRITANNIA', 'IRCTC', 'DLF', 'PERSISTENT', 'SIEMENS', 'INFY', 'NTPC', 'HAVELLS', 'MUTHOOTFIN', 'MRF', 'BALKRISIND', 'POWERGRID', 'ICICIPRULI', 'CANBK', 'CANFINHOME', 'BSOFT', 'NAVINFLUOR', 'GRASIM', 'CHOLAFIN', 'CUMMINSIND', 'GODREJCP', 'APOLLOHOSP', 'RBLBANK', 'OBEROIRLTY', 'COROMANDEL', 'ADANIENT', 'EICHERMOT', 'IDFCFIRSTB', 'SHRIRAMFIN', 'BEL', 'JKCEMENT', 'AXISBANK', 'M&M', 'CIPLA', 'ATUL', 'BATAINDIA', 'GMRINFRA', 'TVSMOTOR', 'ABFRL', 'EXIDEIND', 'AMBUJACEM', 'IPCALAB']

        symbol_list = Symbol.objects.filter(product=product, name__in=option_enables_symbols, is_active=True)

        print(f'Pratik: {log_identifier}: Total Equity Symbol Picked: {len(symbol_list)}')

        for index, symbol_obj in enumerate(symbol_list):
            try:
                nop = len(StockConfig.objects.filter(symbol__product=product, is_active=True))

                mode = None

                entries_list = StockConfig.objects.filter(symbol=symbol_obj, is_active=True)
                if not entries_list:
                    if nop < configuration_obj.open_position:
                        from_day = now - timedelta(days=60)
                        data_frame = historical_data(symbol_obj.token, symbol_obj.exchange, now, from_day, 'ONE_DAY')
                        sleep(0.3)

                        open = data_frame['Open'].iloc[-1]
                        high = data_frame['High'].iloc[-1]
                        low = data_frame['Low'].iloc[-1]
                        close = data_frame['Close'].iloc[-1]
                        max_high = max(data_frame['High'].iloc[-30:-1]) if len(data_frame) >= 32 else max(data_frame['High'].iloc[:-1])
                        min_low = min(data_frame['Low'].iloc[-30:-1]) if len(data_frame) >= 32 else min(data_frame['Low'].iloc[:-1])
                        daily_volatility = calculate_volatility(data_frame)
                            
    
                        if (max_high < high):
                            mode = 'CE'
    
                        # elif (min_low > low):
                        #     mode = 'PE'
    
                        else:
                            mode = None
    
                        if mode not in [None]:
                            data = {
                                'log_identifier': log_identifier,
                                'configuration_obj': configuration_obj,
                                'product': product,
                                'symbol_obj': symbol_obj,
                                'mode': mode,
                                'ltp': close,
                                'target': configuration_obj.target,
                                'stoploss': configuration_obj.stoploss,
                                'fixed_target': configuration_obj.fixed_target,
                                'call_trsl_low': min(data_frame['Low'].iloc[-10:-1]) if len(data_frame) >= 11 else min(data_frame['Low'].iloc[:-1]),
                                'put_trsl_high': max(data_frame['High'].iloc[-10:-1]) if len(data_frame) >= 11 else max(data_frame['High'].iloc[:-1])
                            }
    
                            Price_Action_Trade(data)
                # else:
                #     stock_obj = entries_list[0]
                #     from_day = now - timedelta(days=35)
                #     data_frame = historical_data(symbol_obj.token, symbol_obj.exchange, now, from_day, 'ONE_DAY')

                #     call_trsl_low = min(data_frame['Low'].iloc[-10:-1]) if len(data_frame) >= 11 else min(data_frame['Low'].iloc[:-1])
                #     put_trsl_high = max(data_frame['High'].iloc[-10:-1]) if len(data_frame) >= 11 else max(data_frame['High'].iloc[:-1])

                #     stock_obj.trailing_sl = call_trsl_low if (call_trsl_low > stock_obj.stoploss and call_trsl_low >= stock_obj.trailing_sl) else stock_obj.stoploss if stock_obj.mode == 'CE' else put_trsl_high if (put_trsl_high < stock_obj.stoploss and put_trsl_high <= stock_obj.trailing_sl) else stock_obj.stoploss
                    
                #     stock_obj.tr_hit = True if ((stock_obj.mode == 'CE' and stock_obj.trailing_sl > stock_obj.stoploss) or (stock_obj.mode == 'PE' and stock_obj.trailing_sl < stock_obj.stoploss)) else False
                #     stock_obj.save()
                del mode, entries_list

            except Exception as e:
                StockConfig.objects.filter(symbol=symbol_obj, is_active=False).delete()
                print(f'Pratik: {log_identifier}: Error: in Equity-Symbol: {symbol_obj.name} : {e}')
        del symbol_list

    except Exception as e:
        print(f'Pratik: {log_identifier}: ERROR: Main: {e}')
    print(f'Pratik: {log_identifier}: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True