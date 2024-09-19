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
from trade.settings import BED_URL_DOMAIN, BROKER_API_KEY, BROKER_PIN, BROKER_TOTP_KEY, BROKER_USER_ID, broker_connection, SOCKET_STREAM_URL_DOMAIN


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
        if i['instrumenttype'] in ['OPTSTK'] and (expity_date.month == now.month): # , 'OPTIDX', 'OPTFUT'
            product = 'future'
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
            if product == 'future':
                obj.fno=True
            obj.save()
    future_enables_symbols = set(Symbol.objects.filter(product='future', is_active=True).values_list('name', flat=True))
    Symbol.objects.filter(product='equity', name__in=future_enables_symbols, is_active=True).update(fno=True)
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


def Equity_BreakOut_1(auto_trigger=True):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    product = 'equity'
    log_identifier = 'Equity_BreakOut_1'
    print(f'Pratik: {log_identifier}: Runtime : {product} : {now.strftime("%d-%b-%Y %H:%M:%S")}')

    try:
        if auto_trigger:
            if now.time() < time(9, 18, 00):
                raise Exception("Entry Not Started")
            elif now.time() > time(15, 29, 00):
                raise Exception("Entry Not Stopped")

        configuration_obj = Configuration.objects.filter(product=product)[0]

        option_enables_symbols = ['NESTLEIND', 'LTTS', 'WIPRO', 'M&MFIN', 'PVRINOX', 'SRF', 'SUNTV', 'TECHM', 'ADANIPORTS', 'TCS', 'BIOCON', 'UPL', 'TATACHEM', 'MFSL', 'GODREJPROP', 'DIVISLAB', 'MOTHERSON', 'VEDL', 'ZYDUSLIFE', 'INDIAMART', 'SYNGENE', 'CUB', 'LT', 'ACC', 'HDFCLIFE', 'DRREDDY', 'NATIONALUM', 'LAURUSLABS', 'MARUTI', 'BANKBARODA', 'HINDCOPPER', 'TATACONSUM', 'ABBOTINDIA', 'DIXON', 'BAJFINANCE', 'ASIANPAINT', 'ESCORTS', 'GUJGASLTD', 'INDUSINDBK', 'AARTIIND', 'BHARTIARTL', 'BANDHANBNK', 'SBIN', 'UBL', 'ASTRAL', 'RELIANCE', 'PETRONET', 'GNFC', 'MANAPPURAM', 'GRANULES', 'UNITDSPR', 'SAIL', 'INDIGO', 'TITAN', 'LTF', 'BAJAJFINSV', 'BHEL', 'DABUR', 'INDUSTOWER', 'ONGC', 'TATASTEEL', 'ABCAPITAL', 'ICICIBANK', 'KOTAKBANK', 'ULTRACEMCO', 'COLPAL', 'COALINDIA', 'OFSS', 'MARICO', 'TORNTPHARM', 'CROMPTON', 'SBILIFE', 'BOSCHLTD', 'RAMCOCEM', 'HINDALCO', 'BHARATFORG', 'BPCL', 'GAIL', 'BERGEPAINT', 'ALKEM', 'SUNPHARMA', 'TRENT', 'IDEA', 'HAL', 'PAGEIND', 'VOLTAS', 'LICHSGFIN', 'RECLTD', 'HDFCBANK', 'JSWSTEEL', 'FEDERALBNK', 'ASHOKLEY', 'IOC', 'COFORGE', 'ABB', 'JINDALSTEL', 'LUPIN', 'TATAPOWER', 'INDHOTEL', 'HCLTECH', 'JUBLFOOD', 'SHREECEM', 'IDFC', 'TATACOMM', 'HEROMOTOCO', 'BALRAMCHIN', 'BAJAJ-AUTO', 'LALPATHLAB', 'SBICARD', 'ITC', 'MPHASIS', 'NMDC', 'APOLLOTYRE', 'LTIM', 'MCX', 'PFC', 'PIIND', 'IGL', 'PNB', 'IEX', 'CONCOR', 'GLENMARK', 'DALBHARAT', 'POLYCAB', 'HINDPETRO', 'NAUKRI', 'HDFCAMC', 'ICICIGI', 'MGL', 'AUROPHARMA', 'PEL', 'PIDILITIND', 'TATAMOTORS', 'CHAMBLFERT', 'AUBANK', 'DEEPAKNTR', 'HINDUNILVR', 'METROPOLIS', 'BRITANNIA', 'IRCTC', 'DLF', 'PERSISTENT', 'SIEMENS', 'INFY', 'NTPC', 'HAVELLS', 'MUTHOOTFIN', 'MRF', 'BALKRISIND', 'POWERGRID', 'ICICIPRULI', 'CANBK', 'CANFINHOME', 'BSOFT', 'NAVINFLUOR', 'GRASIM', 'CHOLAFIN', 'CUMMINSIND', 'GODREJCP', 'APOLLOHOSP', 'RBLBANK', 'OBEROIRLTY', 'COROMANDEL', 'ADANIENT', 'EICHERMOT', 'IDFCFIRSTB', 'SHRIRAMFIN', 'BEL', 'JKCEMENT', 'AXISBANK', 'M&M', 'CIPLA', 'ATUL', 'BATAINDIA', 'GMRINFRA', 'TVSMOTOR', 'ABFRL', 'EXIDEIND', 'AMBUJACEM', 'IPCALAB']

        symbol_list = Symbol.objects.filter(product=product, fno=True, is_active=True)

        print(f'Pratik: {log_identifier}: Total Equity Symbol Picked: {len(symbol_list)}')

        new_entry = []
        for index, symbol_obj in enumerate(symbol_list):
            try:
                nop = len(StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=True))

                mode = None

                entries_list = StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=True)
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
                            
    
                        if (max_high < close):
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
                                'fixed_target': configuration_obj.fixed_target
                            }

                            lot = symbol_obj.lot
                            chk_price = close * lot
                            if chk_price < configuration_obj.amount:
                                while True:
                                    chk_price = close * lot
                                    if chk_price >= configuration_obj.amount:
                                        lot = lot - symbol_obj.lot
                                        break
                                    lot += symbol_obj.lot
                                data['lot'] = lot
                                new_entry = Price_Action_Trade(data, new_entry)
                            else:
                                print(f'Pratik: {log_identifier}: Equity-Symbol: Not Enough money to take entry {symbol_obj.name} : {chk_price} : {configuration_obj.amount}')
                del mode, entries_list

            except Exception as e:
                StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=False).delete()
                print(f'Pratik: {log_identifier}: Error: in Equity-Symbol: {symbol_obj.name} : {e}')
        del symbol_list

        # Start Socket Streaming
        if new_entry:
            print(f'Pratik: {data["log_identifier"]}: Total New Entry {len(new_entry)} : New Entries: {new_entry}')
            url = f"{SOCKET_STREAM_URL_DOMAIN}/api/trade/socket-stream/"
            query_params = {
                "symbol": new_entry
            }
            response = requests.get(url, params=query_params, verify=False)
            print(f'Pratik: {data["log_identifier"]}: New Entries: Streaming Response: {response.status_code}')

    except Exception as e:
        print(f'Pratik: {log_identifier}: ERROR: Main: {e}')
    print(f'Pratik: {log_identifier}: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def FnO_BreakOut_1(auto_trigger=True):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    product = 'future'
    log_identifier = 'FnO_BreakOut_1'
    print(f'Pratik: {log_identifier}: Runtime : {product} : {now.strftime("%d-%b-%Y %H:%M:%S")}')

    try:
        if auto_trigger:
            if now.time() < time(9, 18, 00):
                raise Exception("Entry Not Started")
            elif now.time() > time(15, 29, 00):
                raise Exception("Entry Not Stopped")

        configuration_obj = Configuration.objects.filter(product=product)[0]

        symbol_list = Symbol.objects.filter(product='equity', fno=True, is_active=True)

        print(f'Pratik: {log_identifier}: Total FnO Symbol Picked: {len(symbol_list)}')

        new_entry = []
        for index, symbol_obj in enumerate(symbol_list):
            try:
                nop = len(StockConfig.objects.filter(symbol__product=product, is_active=True))

                mode = None

                entries_list = StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=True)
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
                            
    
                        if (max_high < close):
                            mode = 'CE'
                            stock_future_symbol = Symbol.objects.filter(
                                                        product='future',
                                                        name=symbol_obj.name,
                                                        symbol__endswith='CE',
                                                        strike__gt=close,
                                                        fno=True,
                                                        is_active=True).order_by('strike')
    
                        elif (min_low > close):
                            mode = 'PE'
                            stock_future_symbol = Symbol.objects.filter(
                                                        product='future',
                                                        name=symbol_obj.name,
                                                        symbol__endswith='PE',
                                                        strike__lt=close,
                                                        fno=True,
                                                        is_active=True).order_by('-strike')
    
                        else:
                            mode = None
    
                        if mode not in [None]:
                            data = {
                                'log_identifier': log_identifier,
                                'configuration_obj': configuration_obj,
                                'product': product,
                                'mode': mode,
                                'target': configuration_obj.target,
                                'stoploss': configuration_obj.stoploss,
                                'fixed_target': configuration_obj.fixed_target
                            }

                            global broker_connection
                            for fut_sym_obj in stock_future_symbol:
                                ltp = broker_connection.ltpData(fut_sym_obj.exchange, fut_sym_obj.symbol, fut_sym_obj.token)['data']['ltp']
                                lot = fut_sym_obj.lot
                                chk_price = ltp * lot
                                if chk_price < configuration_obj.amount:
                                    while True:
                                        chk_price = ltp * lot
                                        if chk_price >= configuration_obj.amount:
                                            lot = lot - fut_sym_obj.lot
                                            break
                                        lot += fut_sym_obj.lot

                                    data['ltp'] = ltp
                                    data['lot'] = lot
                                    data['symbol_obj'] = fut_sym_obj
                                    new_entry = Price_Action_Trade(data, new_entry)
                                    break

                del mode, entries_list

            except Exception as e:
                StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=False).delete()
                print(f'Pratik: {log_identifier}: Error: in FnO-Symbol: {symbol_obj.name} : {e}')
        del symbol_list

        # Start Socket Streaming
        if new_entry:
            print(f'Pratik: {data["log_identifier"]}: Total New Entry {len(new_entry)} : New Entries: {new_entry}')
            correlation_id = "pratik-socket"
            socket_mode = 1
            nse = []
            nfo = []
            bse = []
            bfo = []
            mcx = []

            for exchange, name, token in new_entry:
                if exchange == 'NSE':
                    nse.append(token)
                elif exchange == 'NFO':
                    nfo.append(token)
                elif exchange == 'BSE':
                    bse.append(token)
                elif exchange == 'BFO':
                    bfo.append(token)
                else:
                    mcx.append(token)

            subscribe_list = []
            for index, i in enumerate((nse,nfo,bse,bfo,mcx)):
                if i:
                    subscribe_list.append({
                        "exchangeType": index+1,
                        "tokens": i
                    })
            url = f"{SOCKET_STREAM_URL_DOMAIN}/api/trade/socket-stream/"
            query_params = {
                "subscribe_list": subscribe_list,
                "correlation_id": correlation_id,
                "socket_mode": socket_mode
            }
            response = requests.get(url, params=query_params, verify=False)
            print(f'Pratik: {data["log_identifier"]}: New Entries: Streaming Response: {response.status_code}')

    except Exception as e:
        print(f'Pratik: {log_identifier}: ERROR: Main: {e}')
    print(f'Pratik: {log_identifier}: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True
