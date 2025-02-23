import pyotp
import requests
import threading
import yfinance as yf
from time import sleep
from zoneinfo import ZoneInfo
from SmartApi import SmartConnect
from helper.emails import email_send
from account.action import UserTrade
from helper.common import last_thursday
from datetime import datetime, time, timedelta
from helper.angel_function import historical_data
from stock.models import StockConfig, Transaction
from helper.indicator import BB, PIVOT, SUPER_TREND
from system_conf.models import Configuration, Symbol
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from helper.angel_socket import LTP_Action, connect_to_socket
from helper.trade_action import Price_Action_Trade, Stock_Square_Off
from account.models import AccountConfiguration, AccountKeys, AccountStockConfig, AccountTransaction
from trade_bros.settings import sws, open_position, BED_URL_DOMAIN, BROKER_API_KEY, BROKER_PIN, BROKER_TOTP_KEY, BROKER_USER_ID, broker_connection, account_connections, entry_holder, RENDER_KEY


def stay_awake():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'Stay Awake: Runtime: {now.strftime("%d-%b-%Y %H:%M:%S")}')
    url = f"{BED_URL_DOMAIN}/api/system_conf/awake/"
    x = requests.get(url, verify=False)
    print(f'Stay Awake: Execution Time(hh:mm:ss): {url} : {x.status_code} : {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def NotifyUsers():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'TradeBros: Notify User: Started')
    user_obj_list = AccountKeys.objects.filter(is_active=True)

    print(f'TradeBros: Notify User: Total User: {user_obj_list.count()}')
    for user in user_obj_list:
        try:
            invested_value = 0
            current_value = 0
            entries = AccountStockConfig.objects.filter(account=user)
            for i in entries:
                stock_obj = StockConfig.objects.get(symbol__symbol=i.symbol)
                current_value += i.lot * stock_obj.ltp
                invested_value += i.lot * stock_obj.price
            pnl = (current_value - invested_value)/invested_value * 100

            if invested_value > 0:
                # Send Email Notification
                template = 'portfolio_notification.html'
                subject = f"{user.user_id}-{user.first_name}'s Portfolio on TradeBros.AI"
                recipients = [user.email]
                email_context = {
                    "name": user.first_name,
                    "today": now.strftime("%d-%b-%Y"),
                    "flag_return": True if pnl > 0 else False,
                    "percent": round(pnl, 2),
                    "current_value": round(current_value, 2),
                    "invested_value": round(invested_value, 2),
                    "position": entries.count()
                }
                email_send(subject, template, recipients, email_context)
                print(f'TradeBros: Notify User: Notified to: {user.first_name} : {user.email}')
        except Exception as e:
            print(f'TradeBros: Notify User: Loop Error: {e}')
    print(f'TradeBros: Notify User: Ended')
    print(f'TradeBros: Notify User: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def MarketDataUpdate(auto_trigger=True):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        print(f'TradeBros: Market data Update: Started : Runtime : {now.strftime("%d-%b-%Y %H:%M:%S")}')
        if now.time().minute in list(range(0, 60, 5)):
            sleep(10)
        nse_tokens = list(Symbol.objects.filter(exchange='NSE', is_active=True).values_list('token', flat=True))
        token_list = [nse_tokens[x:x+50] for x in range(0, len(nse_tokens), 50)]
        global broker_connection
        for list_ in token_list:
            try:
                data = broker_connection.getMarketData(mode="FULL", exchangeTokens={"NSE": list_})
                if data.get('data'):
                    fetched = data.get('data')['fetched']
                    for i in fetched:
                        if (now.time() > time(8, 00, 00) and now.time() < time(9, 14, 00)) or not auto_trigger:
                            Symbol.objects.filter(token=i['symbolToken'],
                                                    is_active=True).update(
                                                        volume=i['tradeVolume'],
                                                        oi=i['opnInterest'],
                                                        percentchange=i['percentChange'],
                                                        valuechange=i['netChange'],
                                                        ltp=i['ltp'],
                                                        weekhigh52=i['52WeekHigh'],
                                                        weeklow52=i['52WeekLow']
                                                    )
                        else:
                            Symbol.objects.filter(token=i['symbolToken'],
                                                    is_active=True).update(
                                                        volume=i['tradeVolume'],
                                                        oi=i['opnInterest'],
                                                        percentchange=i['percentChange'],
                                                        valuechange=i['netChange'],
                                                        ltp=i['ltp']
                                                    )
                sleep(1)
            except Exception as e:
                print(f'TradeBros: Market data Update: Loop Error: {e}')
    except Exception as e:
        print(f'TradeBros: Market data Update: Main Error: {e}')
    print(f'TradeBros: Market data Update: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def SymbolSetup():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        print(f'TradeBros: Symbol Setup: Started')
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        data = requests.get(url).json()

        open_entries_symbols = StockConfig.objects.filter(is_active=True).values_list('symbol__symbol', flat=True)
        Symbol.objects.filter(is_active=True).exclude(symbol__in=open_entries_symbols).delete()

        Symbol.objects.filter(expiry__lt=now.date(), is_active=True).delete()

        exclude_symbol = ['HDFCNIFTY', '031NSETEST', '151NSETEST', 'LIQUID', 'HNGSNGBEES', 'AXISCETF', 'SETFNIFBK', 'EBANKNIFTY', '171NSETEST', 'SETFNIF50', 'CPSEETF', 'GSEC10IETF', 'DIVOPPBEES', 'OILIETF', 'AUTOIETF', 'HDFCLIQUID', 'AXISNIFTY', 'NIFTY50ADD', 'CONSUMBEES', 'HDFCNIFBAN', 'NIFTYBEES', '101NSETEST', 'LIQUIDETF', 'TOP10ADD', 'NIF100BEES', 'PSUBNKIETF', 'INFRABEES', 'AXISTECETF', 'NV20BEES', 'ALPL30IETF', 'INFRAIETF', '181NSETEST', 'MOM30IETF', 'SBISILVER', 'NIFTY1', 'UTINIFTETF', 'SILVERBEES', 'BANKETFADD', 'MIDCAPIETF', 'PHARMABEES', 'SENSEXADD', 'GOLDCASE', 'HEALTHIETF', 'BSLNIFTY', 'PVTBANIETF', 'BSE500IETF', '071NSETEST', '011NSETEST', 'IVZINGOLD', 'NETF', 'SENSEXIETF', 'SBIETFIT', 'ABSLBANETF', 'SILVERTUC', 'SHARIABEES', 'EBBETF0433', 'SILVERETF', 'FMCGIETF', 'NIF10GETF', '021NSETEST', 'CONSUMIETF', 'SILVERIETF', 'SETF10GILT', 'NV20IETF', 'SDL26BEES', 'SENSEXETF', 'NIF100IETF', 'QNIFTY', 'MIDSELIETF', 'BBNPPGOLD', 'SBINEQWETF', 'NIFTYIETF', 'LIQUIDIETF', 'ITBEES', 'LICNETFSEN', '121NSETEST', '051NSETEST', 'ITETF', 'NIFTYETF', 'SILVER', 'EQUAL50ADD', 'UTISENSETF', 'QUAL30IETF', 'AXISGOLD', 'AXISHCETF', 'ALPHAETF', 'HDFCNIF100', 'PSUBNKBEES', 'BSLSENETFG', '041NSETEST', 'QGOLDHALF', 'BBETF0432', 'COMMOIETF', 'MONIFTY500', 'BBNPNBETF', 'LIQUIDCASE', 'GINNIFILA', 'GOLDIAM', 'NAVINIFTY', 'ITIETF', 'SILVER1', '131NSETEST', 'SBIETFPB', 'LICNETFN50', 'BANKBEES', 'METALIETF', 'AUTOBEES', 'ITETFADD', 'SILVERADD', 'HEALTHADD', 'GOLDSHARE', 'LIQUID1', 'AXISBPSETF', 'IVZINNIFTY', 'GILT5YBEES', '111NSETEST', 'HDFCGOLD', 'SILVRETF', 'GOLDTECH', 'BANKETF', 'LICNETFGSC', 'LTGILTBEES', 'GOLD1', 'BANKNIFTY1', '161NSETEST', 'ABSLLIQUID', 'GSEC5IETF', 'LIQUIDBETF', '061NSETEST', 'BANKIETF', 'LIQUIDSHRI', 'AXISILVER', 'UTIBANKETF', 'IDFNIFTYET', 'MIDCAPETF', 'GOLDBEES', 'FINIETF', 'EBBETF0425', 'PVTBANKADD', 'NEXT50IETF', 'ESILVER', 'GOLDETFADD', 'BANKBETF', 'JUNIORBEES', 'PSUBANKADD', 'MIDQ50ADD', 'HDFCNIFIT', 'GOLDIETF', 'EBBETF0430', 'NIF5GETF', 'BSLGOLDETF', 'EBBETF0431', 'LIQUIDSBI', 'EGOLD', 'TATAGOLD', 'TNIDETF', 'SBIETFQLTY', 'NIFITETF', 'LOWVOLIETF', 'SDL24BEES', '081NSETEST', 'GOLDETF', 'SETFGOLD', 'AXISBNKETF', 'NIFTYQLITY', 'LIQUIDADD', '141NSETEST', 'SBIETFCON', 'LIQUIDBEES', 'MID150BEES', 'SETFNN50', 'NIFMID150', '091NSETEST', 'HDFCSILVER', 'NIFTYBETF', 'LICMFGOLD', 'MOM100', 'TOP100CASE', 'MON100', 'LICNMID100', 'MIDSMALL', 'MIDCAP', 'MID150CASE', 'HDFCMID150', 'HDFCNEXT50', 'UTISXN50', 'MONQ50', 'MOM50', 'ABSLNN50ET', 'HDFCSML250', 'NEXT50', 'HDFCBSE500', 'MOSMALL250', 'UTINEXT50', 'MASPTOP50', 'HDFCSENSEX', 'AXSENSEX', '11NSETEST', 'MOQLTYINAV', 'MOVALUINAV', 'N1NSETEST', 'V1NSETEST', 'G1NSETEST', 'VAL30IETF']

        print(f'TradeBros: Symbol Setup: Fetch Index Symbol List : Started')

        nifty50 = ['ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BEL', 'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DRREDDY', 'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ICICIBANK', 'ITC', 'INDUSINDBK', 'INFY', 'JSWSTEEL', 'KOTAKBANK', 'LT', 'M&M', 'MARUTI', 'NTPC', 'NESTLEIND', 'ONGC', 'POWERGRID', 'RELIANCE', 'SBILIFE', 'SHRIRAMFIN', 'SBIN', 'SUNPHARMA', 'TCS', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TITAN', 'TRENT', 'ULTRACEMCO', 'WIPRO']
        
        nifty100 = ['ABB', 'ADANIENSOL', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS', 'ADANIPOWER', 'ATGL', 'AMBUJACEM', 'APOLLOHOSP', 'ASIANPAINT', 'DMART', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BAJAJHLDNG', 'BANKBARODA', 'BEL', 'BHEL', 'BPCL', 'BHARTIARTL', 'BOSCHLTD', 'BRITANNIA', 'CANBK', 'CHOLAFIN', 'CIPLA', 'COALINDIA', 'DLF', 'DABUR', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'GAIL', 'GODREJCP', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE', 'HAVELLS', 'HEROMOTOCO', 'HINDALCO', 'HAL', 'HINDUNILVR', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'ITC', 'IOC', 'IRCTC', 'IRFC', 'INDUSINDBK', 'NAUKRI', 'INFY', 'INDIGO', 'JSWENERGY', 'JSWSTEEL', 'JINDALSTEL', 'JIOFIN', 'KOTAKBANK', 'LTIM', 'LT', 'LICI', 'LODHA', 'M&M', 'MARUTI', 'NHPC', 'NTPC', 'NESTLEIND', 'ONGC', 'PIDILITIND', 'PFC', 'POWERGRID', 'PNB', 'RECLTD', 'RELIANCE', 'SBILIFE', 'MOTHERSON', 'SHREECEM', 'SHRIRAMFIN', 'SIEMENS', 'SBIN', 'SUNPHARMA', 'TVSMOTOR', 'TCS', 'TATACONSUM', 'TATAMOTORS', 'TATAPOWER', 'TATASTEEL', 'TECHM', 'TITAN', 'TORNTPHARM', 'TRENT', 'ULTRACEMCO', 'UNIONBANK', 'UNITDSPR', 'VBL', 'VEDL', 'WIPRO', 'ZOMATO', 'ZYDUSLIFE']
        
        nifty200 = ['ABB', 'ACC', 'APLAPOLLO', 'AUBANK', 'ADANIENSOL', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS', 'ADANIPOWER', 'ATGL', 'ABCAPITAL', 'ABFRL', 'ALKEM', 'AMBUJACEM', 'APOLLOHOSP', 'APOLLOTYRE', 'ASHOKLEY', 'ASIANPAINT', 'ASTRAL', 'AUROPHARMA', 'DMART', 'AXISBANK', 'BSE', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BAJAJHLDNG', 'BALKRISIND', 'BANDHANBNK', 'BANKBARODA', 'BANKINDIA', 'MAHABANK', 'BDL', 'BEL', 'BHARATFORG', 'BHEL', 'BPCL', 'BHARTIARTL', 'BHARTIHEXA', 'BIOCON', 'BOSCHLTD', 'BRITANNIA', 'CGPOWER', 'CANBK', 'CHOLAFIN', 'CIPLA', 'COALINDIA', 'COCHINSHIP', 'COFORGE', 'COLPAL', 'CONCOR', 'CUMMINSIND', 'DLF', 'DABUR', 'DELHIVERY', 'DIVISLAB', 'DIXON', 'DRREDDY', 'EICHERMOT', 'ESCORTS', 'EXIDEIND', 'NYKAA', 'FEDERALBNK', 'FACT', 'GAIL', 'GMRINFRA', 'GODREJCP', 'GODREJPROP', 'GRASIM', 'HCLTECH', 'HDFCAMC', 'HDFCBANK', 'HDFCLIFE', 'HAVELLS', 'HEROMOTOCO', 'HINDALCO', 'HAL', 'HINDPETRO', 'HINDUNILVR', 'HINDZINC', 'HUDCO', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'IDBI', 'IDFCFIRSTB', 'IRB', 'ITC', 'INDIANB', 'INDHOTEL', 'IOC', 'IOB', 'IRCTC', 'IRFC', 'IREDA', 'IGL', 'INDUSTOWER', 'INDUSINDBK', 'NAUKRI', 'INFY', 'INDIGO', 'JSWENERGY', 'JSWINFRA', 'JSWSTEEL', 'JINDALSTEL', 'JIOFIN', 'JUBLFOOD', 'KPITTECH', 'KALYANKJIL', 'KOTAKBANK', 'LTF', 'LICHSGFIN', 'LTIM', 'LT', 'LICI', 'LUPIN', 'MRF', 'LODHA', 'M&MFIN', 'M&M', 'MRPL', 'MANKIND', 'MARICO', 'MARUTI', 'MFSL', 'MAXHEALTH', 'MAZDOCK', 'MPHASIS', 'MUTHOOTFIN', 'NHPC', 'NLCINDIA', 'NMDC', 'NTPC', 'NESTLEIND', 'OBEROIRLTY', 'ONGC', 'OIL', 'PAYTM', 'OFSS', 'POLICYBZR', 'PIIND', 'PAGEIND', 'PATANJALI', 'PERSISTENT', 'PETRONET', 'PHOENIXLTD', 'PIDILITIND', 'POLYCAB', 'POONAWALLA', 'PFC', 'POWERGRID', 'PRESTIGE', 'PNB', 'RECLTD', 'RVNL', 'RELIANCE', 'SBICARD', 'SBILIFE', 'SJVN', 'SRF', 'MOTHERSON', 'SHREECEM', 'SHRIRAMFIN', 'SIEMENS', 'SOLARINDS', 'SONACOMS', 'SBIN', 'SAIL', 'SUNPHARMA', 'SUNDARMFIN', 'SUPREMEIND', 'SUZLON', 'TVSMOTOR', 'TATACHEM', 'TATACOMM', 'TCS', 'TATACONSUM', 'TATAELXSI', 'TATAMOTORS', 'TATAPOWER', 'TATASTEEL', 'TATATECH', 'TECHM', 'TITAN', 'TORNTPHARM', 'TORNTPOWER', 'TRENT', 'TIINDIA', 'UPL', 'ULTRACEMCO', 'UNIONBANK', 'UNITDSPR', 'VBL', 'VEDL', 'IDEA', 'VOLTAS', 'WIPRO', 'YESBANK', 'ZOMATO', 'ZYDUSLIFE']

        midcpnifty50 = ['ACC', 'APLAPOLLO', 'AUBANK', 'ABCAPITAL', 'ALKEM', 'ASHOKLEY', 'ASTRAL', 'AUROPHARMA', 'BHARATFORG', 'CGPOWER', 'COLPAL', 'CONCOR', 'CUMMINSIND', 'DIXON', 'FEDERALBNK', 'GMRINFRA', 'GODREJPROP', 'HDFCAMC', 'HINDPETRO', 'IDFCFIRSTB', 'INDHOTEL', 'INDUSTOWER', 'KPITTECH', 'LTF', 'LUPIN', 'MRF', 'MARICO', 'MAXHEALTH', 'MPHASIS', 'MUTHOOTFIN', 'NMDC', 'OBEROIRLTY', 'OFSS', 'POLICYBZR', 'PIIND', 'PERSISTENT', 'PETRONET', 'PHOENIXLTD', 'POLYCAB', 'SBICARD', 'SRF', 'SAIL', 'SUNDARMFIN', 'SUPREMEIND', 'SUZLON', 'TATACOMM', 'UPL', 'IDEA', 'VOLTAS', 'YESBANK']
        
        midcpnifty100 = ['ACC', 'APLAPOLLO', 'AUBANK', 'ABCAPITAL', 'ABFRL', 'ALKEM', 'APOLLOTYRE', 'ASHOKLEY', 'ASTRAL', 'AUROPHARMA', 'BSE', 'BALKRISIND', 'BANDHANBNK', 'BANKINDIA', 'MAHABANK', 'BDL', 'BHARATFORG', 'BHARTIHEXA', 'BIOCON', 'CGPOWER', 'COCHINSHIP', 'COFORGE', 'COLPAL', 'CONCOR', 'CUMMINSIND', 'DELHIVERY', 'DIXON', 'ESCORTS', 'EXIDEIND', 'NYKAA', 'FEDERALBNK', 'FACT', 'GMRINFRA', 'GODREJPROP', 'HDFCAMC', 'HINDPETRO', 'HINDZINC', 'HUDCO', 'IDBI', 'IDFCFIRSTB', 'IRB', 'INDIANB', 'INDHOTEL', 'IOB', 'IREDA', 'IGL', 'INDUSTOWER', 'JSWINFRA', 'JUBLFOOD', 'KPITTECH', 'KALYANKJIL', 'LTF', 'LICHSGFIN', 'LUPIN', 'MRF', 'M&MFIN', 'MRPL', 'MANKIND', 'MARICO', 'MFSL', 'MAXHEALTH', 'MAZDOCK', 'MPHASIS', 'MUTHOOTFIN', 'NLCINDIA', 'NMDC', 'OBEROIRLTY', 'OIL', 'PAYTM', 'OFSS', 'POLICYBZR', 'PIIND', 'PAGEIND', 'PATANJALI', 'PERSISTENT', 'PETRONET', 'PHOENIXLTD', 'POLYCAB', 'POONAWALLA', 'PRESTIGE', 'RVNL', 'SBICARD', 'SJVN', 'SRF', 'SOLARINDS', 'SONACOMS', 'SAIL', 'SUNDARMFIN', 'SUPREMEIND', 'SUZLON', 'TATACHEM', 'TATACOMM', 'TATAELXSI', 'TATATECH', 'TORNTPOWER', 'TIINDIA', 'UPL', 'IDEA', 'VOLTAS', 'YESBANK']
        
        midcpnifty150 = ['3MINDIA', 'ACC', 'AIAENG', 'APLAPOLLO', 'AUBANK', 'ABBOTINDIA', 'AWL', 'ABCAPITAL', 'ABFRL', 'AJANTPHARM', 'ALKEM', 'APOLLOTYRE', 'ASHOKLEY', 'ASTRAL', 'AUROPHARMA', 'BSE', 'BALKRISIND', 'BANDHANBNK', 'BANKINDIA', 'MAHABANK', 'BAYERCROP', 'BERGEPAINT', 'BDL', 'BHARATFORG', 'BHARTIHEXA', 'BIOCON', 'CGPOWER', 'CRISIL', 'CARBORUNIV', 'COCHINSHIP', 'COFORGE', 'COLPAL', 'CONCOR', 'COROMANDEL', 'CUMMINSIND', 'DALBHARAT', 'DEEPAKNTR', 'DELHIVERY', 'DIXON', 'EMAMILTD', 'ENDURANCE', 'ESCORTS', 'EXIDEIND', 'NYKAA', 'FEDERALBNK', 'FACT', 'FORTIS', 'GMRINFRA', 'GICRE', 'GLAND', 'GLAXO', 'MEDANTA', 'GODREJIND', 'GODREJPROP', 'GRINDWELL', 'FLUOROCHEM', 'GUJGASLTD', 'HDFCAMC', 'HINDPETRO', 'HINDZINC', 'POWERINDIA', 'HONAUT', 'HUDCO', 'IDBI', 'IDFCFIRSTB', 'IRB', 'INDIANB', 'INDHOTEL', 'IOB', 'IREDA', 'IGL', 'INDUSTOWER', 'IPCALAB', 'JKCEMENT', 'JSWINFRA', 'JSL', 'JUBLFOOD', 'KPRMILL', 'KEI', 'KPITTECH', 'KALYANKJIL', 'LTF', 'LTTS', 'LICHSGFIN', 'LINDEINDIA', 'LLOYDSME', 'LUPIN', 'MRF', 'M&MFIN', 'MRPL', 'MANKIND', 'MARICO', 'MFSL', 'MAXHEALTH', 'MAZDOCK', 'METROBRAND', 'MSUMI', 'MPHASIS', 'MUTHOOTFIN', 'NLCINDIA', 'NMDC', 'NAM-INDIA', 'OBEROIRLTY', 'OIL', 'PAYTM', 'OFSS', 'POLICYBZR', 'PIIND', 'PAGEIND', 'PATANJALI', 'PERSISTENT', 'PETRONET', 'PHOENIXLTD', 'POLYCAB', 'POONAWALLA', 'PRESTIGE', 'PGHH', 'RVNL', 'SBICARD', 'SJVN', 'SKFINDIA', 'SRF', 'SCHAEFFLER', 'SOLARINDS', 'SONACOMS', 'STARHEALTH', 'SAIL', 'SUNTV', 'SUNDARMFIN', 'SUNDRMFAST', 'SUPREMEIND', 'SUZLON', 'SYNGENE', 'TATACHEM', 'TATACOMM', 'TATAELXSI', 'TATAINVEST', 'TATATECH', 'NIACL', 'THERMAX', 'TIMKEN', 'TORNTPOWER', 'TIINDIA', 'UNOMINDA', 'UPL', 'UBL', 'IDEA', 'VOLTAS', 'YESBANK', 'ZFCVINDIA']
        
        smallcpnifty50 = ['360ONE', 'AARTIIND', 'ARE&M', 'ANGELONE', 'APARINDS', 'ATUL', 'BSOFT', 'BLUESTARCO', 'BRIGADE', 'CESC', 'CASTROLIND', 'CDSL', 'CENTURYTEX', 'CAMS', 'CROMPTON', 'CYIENT', 'FINCABLES', 'GLENMARK', 'GESHIP', 'GSPL', 'HFCL', 'HINDCOPPER', 'IDFC', 'IIFL', 'INDIAMART', 'IEX', 'KPIL', 'KARURVYSYA', 'LAURUSLABS', 'MGL', 'MANAPPURAM', 'MCX', 'NATCOPHARM', 'NBCC', 'NCC', 'NH', 'NATIONALUM', 'NAVINFLUOR', 'PNBHOUSING', 'PVRINOX', 'PEL', 'PPLPHARMA', 'RBLBANK', 'RKFORGE', 'REDINGTON', 'SONATSOFTW', 'TEJASNET', 'RAMCOCEM', 'ZEEL', 'ZENSARTECH']
        
        smallcpnifty100 = ['360ONE', 'AADHARHFC', 'AARTIIND', 'AAVAS', 'ACE', 'AEGISLOG', 'AFFLE', 'ARE&M', 'AMBER', 'ANGELONE', 'APARINDS', 'ASTERDM', 'ATUL', 'BEML', 'BLS', 'BATAINDIA', 'BSOFT', 'BLUESTARCO', 'BRIGADE', 'CESC', 'CASTROLIND', 'CENTRALBK', 'CDSL', 'CENTURYTEX', 'CHAMBLFERT', 'CHENNPETRO', 'CAMS', 'CREDITACC', 'CROMPTON', 'CYIENT', 'DATAPATTNS', 'LALPATHLAB', 'FINCABLES', 'FSL', 'FIVESTAR', 'GRSE', 'GLENMARK', 'GODIGIT', 'GESHIP', 'GMDCLTD', 'GSPL', 'HBLPOWER', 'HFCL', 'HAPPSTMNDS', 'HINDCOPPER', 'IDFC', 'IFCI', 'IIFL', 'IRCON', 'ITI', 'INDIAMART', 'IEX', 'INOXWIND', 'INTELLECT', 'JBMA', 'J&KBANK', 'JWL', 'JYOTHYLAB', 'KPIL', 'KARURVYSYA', 'KAYNES', 'KEC', 'LAURUSLABS', 'MGL', 'MANAPPURAM', 'MCX', 'NATCOPHARM', 'NBCC', 'NCC', 'NSLNISP', 'NH', 'NATIONALUM', 'NAVINFLUOR', 'OLECTRA', 'PNBHOUSING', 'PVRINOX', 'PEL', 'PPLPHARMA', 'RBLBANK', 'RITES', 'RADICO', 'RKFORGE', 'RAYMOND', 'REDINGTON', 'SHYAMMETL', 'SIGNATURE', 'SONATSOFTW', 'SWSOLAR', 'SWANENERGY', 'TANLA', 'TTML', 'TEJASNET', 'RAMCOCEM', 'TITAGARH', 'TRIDENT', 'TRITURBINE', 'UCOBANK', 'WELSPUNLIV', 'ZEEL', 'ZENSARTECH']
        
        smallcpnifty250 = ['360ONE', 'AADHARHFC', 'AARTIIND', 'AAVAS', 'ACE', 'ABSLAMC', 'AEGISLOG', 'AFFLE', 'APLLTD', 'ALKYLAMINE', 'ALOKINDS', 'ARE&M', 'AMBER', 'ANANDRATHI', 'ANANTRAJ', 'ANGELONE', 'APARINDS', 'APTUS', 'ACI', 'ASAHIINDIA', 'ASTERDM', 'ASTRAZEN', 'ATUL', 'AVANTIFEED', 'BASF', 'BEML', 'BLS', 'BALAMINES', 'BALRAMCHIN', 'BATAINDIA', 'BIKAJI', 'BIRLACORPN', 'BSOFT', 'BLUEDART', 'BLUESTARCO', 'BBTC', 'BRIGADE', 'MAPMYINDIA', 'CCL', 'CESC', 'CIEINDIA', 'CAMPUS', 'CANFINHOME', 'CAPLIPOINT', 'CGCL', 'CASTROLIND', 'CEATLTD', 'CELLO', 'CENTRALBK', 'CDSL', 'CENTURYPLY', 'CENTURYTEX', 'CERA', 'CHALET', 'CHAMBLFERT', 'CHEMPLASTS', 'CHENNPETRO', 'CHOLAHLDNG', 'CUB', 'CLEAN', 'CAMS', 'CONCORDBIO', 'CRAFTSMAN', 'CREDITACC', 'CROMPTON', 'CYIENT', 'DOMS', 'DATAPATTNS', 'DEEPAKFERT', 'DEVYANI', 'LALPATHLAB', 'EIDPARRY', 'EIHOTEL', 'EASEMYTRIP', 'ELECON', 'ELGIEQUIP', 'ENGINERSIN', 'EQUITASBNK', 'ERIS', 'FINEORG', 'FINCABLES', 'FINPIPE', 'FSL', 'FIVESTAR', 'GRINFRA', 'GET&D', 'GRSE', 'GILLETTE', 'GLENMARK', 'GODIGIT', 'GPIL', 'GODFRYPHLP', 'GODREJAGRO', 'GRANULES', 'GRAPHITE', 'GESHIP', 'GAEL', 'GMDCLTD', 'GNFC', 'GPPL', 'GSFC', 'GSPL', 'HEG', 'HBLPOWER', 'HFCL', 'HAPPSTMNDS', 'HSCL', 'HINDCOPPER', 'HOMEFIRST', 'HONASA', 'ISEC', 'IDFC', 'IFCI', 'IIFL', 'INOXINDIA', 'IRCON', 'ITI', 'INDGN', 'INDIACEM', 'INDIAMART', 'IEX', 'INOXWIND', 'INTELLECT', 'JBCHEPHARM', 'JBMA', 'JKLAKSHMI', 'JKTYRE', 'JMFINANCIL', 'JPPOWER', 'J&KBANK', 'JINDALSAW', 'JUBLINGREA', 'JUBLPHARMA', 'JWL', 'JUSTDIAL', 'JYOTHYLAB', 'JYOTICNC', 'KNRCON', 'KSB', 'KAJARIACER', 'KPIL', 'KANSAINER', 'KARURVYSYA', 'KAYNES', 'KEC', 'KFINTECH', 'KIRLOSBROS', 'KIRLOSENG', 'KIMS', 'LATENTVIEW', 'LAURUSLABS', 'LEMONTREE', 'MMTC', 'MGL', 'MAHSEAMLES', 'MAHLIFE', 'MANAPPURAM', 'MASTEK', 'METROPOLIS', 'MINDACORP', 'MOTILALOFS', 'MCX', 'NATCOPHARM', 'NBCC', 'NCC', 'NSLNISP', 'NH', 'NATIONALUM', 'NAVINFLUOR', 'NETWEB', 'NETWORK18', 'NEWGEN', 'NUVAMA', 'NUVOCO', 'OLECTRA', 'PCBL', 'PNBHOUSING', 'PNCINFRA', 'PTCIL', 'PVRINOX', 'PFIZER', 'PEL', 'PPLPHARMA', 'POLYMED', 'PRAJIND', 'QUESS', 'RRKABEL', 'RBLBANK', 'RHIM', 'RITES', 'RADICO', 'RAILTEL', 'RAINBOW', 'RAJESHEXPO', 'RKFORGE', 'RCF', 'RATNAMANI', 'RTNINDIA', 'RAYMOND', 'REDINGTON', 'ROUTE', 'SBFC', 'SAMMAANCAP', 'SANOFI', 'SAPPHIRE', 'SAREGAMA', 'SCHNEIDER', 'SCI', 'RENUKA', 'SHYAMMETL', 'SIGNATURE', 'SOBHA', 'SONATSOFTW', 'SWSOLAR', 'SUMICHEM', 'SPARC', 'SUVENPHAR', 'SWANENERGY', 'SYRMA', 'TBOTEK', 'TV18BRDCST', 'TVSSCS', 'TANLA', 'TTML', 'TECHNOE', 'TEJASNET', 'RAMCOCEM', 'TITAGARH', 'TRIDENT', 'TRIVENI', 'TRITURBINE', 'UCOBANK', 'UTIAMC', 'UJJIVANSFB', 'USHAMART', 'VGUARD', 'VIPIND', 'DBREALTY', 'VTL', 'VARROC', 'MANYAVAR', 'VIJAYA', 'VINATIORGA', 'WELCORP', 'WELSPUNLIV', 'WESTLIFE', 'WHIRLPOOL', 'ZEEL', 'ZENSARTECH', 'ECLERX']

        print(f'TradeBros: Symbol Setup: Fetch Index Symbol List : Ended')

        last_thursday_date = last_thursday(now)
        if last_thursday_date.date() < now.date():
            month_num = now.month + 1
        else:
            month_num = now.month

        exist_token_symbols = list(Symbol.objects.filter(is_active=True).values_list('token', flat=True))

        bulk_create_list = []
        processed_token = []
        for i in data:
            product = None
            expity_date = datetime.strptime(i['expiry'], '%d%b%Y') if i['expiry'] else None
            if i['exch_seg'] in ['NSE', 'NFO']:# and i['name'] not in exclude_symbol:
                if i['instrumenttype'] in ['OPTSTK', 'OPTIDX'] and (expity_date.month == month_num) and (expity_date.date() > now.date()): # , 'OPTIDX', 'OPTFUT'
                    product = 'future'
                elif (i['symbol'] in ['Nifty 50', 'Nifty Bank', 'NIFTY MID SELECT', 'Nifty Fin Service', 'Nifty Next 50'] and expity_date == None) or i['symbol'].endswith('-EQ'):
                    product = 'equity'
                if product is not None:
                    if i['token'] not in exist_token_symbols and i['token'] not in processed_token:
                        bulk_create_list.append(
                            Symbol(
                                product=product,
                                name=i['name'],
                                symbol=i['symbol'],
                                token=i['token'],
                                strike=int(i['strike'].split('.')[0])/100,
                                exchange=i['exch_seg'],
                                expiry=expity_date,
                                lot=int(i['lotsize']),
                                fno=True if product == 'future' else False,
                                nifty50=True if i['name'] in nifty50 else False,
                                nifty100=True if i['name'] in nifty100 else False,
                                nifty200=True if i['name'] in nifty200 else False,
                                midcpnifty50=True if i['name'] in midcpnifty50 else False,
                                midcpnifty100=True if i['name'] in midcpnifty100 else False,
                                midcpnifty150=True if i['name'] in midcpnifty150 else False,
                                smallcpnifty50=True if i['name'] in smallcpnifty50 else False,
                                smallcpnifty100=True if i['name'] in smallcpnifty100 else False,
                                smallcpnifty250=True if i['name'] in smallcpnifty250 else False
                            )
                        )
                        processed_token.append(i['token'])
            if len(bulk_create_list) == 1000:
                Symbol.objects.bulk_create(bulk_create_list)
                print(f"TradeBros: Symbol Setup: {Symbol.objects.filter(is_active=True).count()}")
                bulk_create_list = []
        Symbol.objects.bulk_create(bulk_create_list)
        print(f"TradeBros: Symbol Setup: Loop Ended")

        future_enables_symbols = set(Symbol.objects.filter(product='future', is_active=True).values_list('name', flat=True))
        Symbol.objects.filter(product='equity', name__in=future_enables_symbols, is_active=True).update(fno=True)
    except Exception as e:
        print(f'TradeBros: Symbol Setup: Main Error: {e}')
    print(f'TradeBros: Symbol Setup: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def AccountConnection():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        print(f'TradeBros: Account Connection: Started')
        global account_connections
        try:
            print(f'TradeBros: Account Connection: Terminate Session for accounts: Started')
            for user_id_conn in account_connections:
                account_connections[user_id_conn].terminateSession(user_id_conn)
                print(f'TradeBros: Account Connection: Terminated Session for accounts: {user_id_conn}')
            print(f'TradeBros: Account Connection: Terminate Session for accounts: Ended')
            sleep(5)
        except Exception as e:
            print(f'TradeBros: Account Connection: Terminate Session for accounts: Error: {e}')
        
        print(f'TradeBros: Account Connection: Generate Session for accounts: Started')
        user_accounts = AccountKeys.objects.filter(is_active=True)

        for user_account_obj in user_accounts:
            connection = SmartConnect(api_key=user_account_obj.api_key)
            connection.generateSession(user_account_obj.user_id, user_account_obj.user_pin, totp=pyotp.TOTP(user_account_obj.totp_key).now())
            account_connections[user_account_obj.user_id] = connection

            # Get Account Detail
            account_detail = connection.getProfile(connection.refresh_token)
            if account_detail['message'] == 'SUCCESS':
                # Get Funds detail
                if now.time() < time(9, 14, 00):
                    fund_detail = connection.rmsLimit()
                    if fund_detail['message'] == 'SUCCESS':
                        account_config, _ = AccountConfiguration.objects.get_or_create(account=user_account_obj)
                        account_config.account_balance = float(fund_detail['data']['availablecash'])
                        if account_config.total_open_position > account_config.active_open_position:
                            if account_config.account_balance <= 10:
                                account_config.account_balance = 100000
                                account_config.entry_amount = 10000
                            else:
                                account_config.entry_amount = float(fund_detail['data']['availablecash'])/(account_config.total_open_position-account_config.active_open_position)
                            account_config.save()

                print(f'TradeBros: Account Connection: Session generated for {account_detail["data"]["name"]} : {account_detail["data"]["clientcode"]}')
            else:
                print(f'TradeBros: Account Connection: failed to generated session for {user_account_obj.first_name} {user_account_obj.last_name} : {user_account_obj.user_id}')

        print(f'TradeBros: Account Connection: Generate Session for accounts: Ended')
    except Exception as e:
        print(f'TradeBros: Account Connection: Error: {e}')
    print(f'TradeBros: Account Connection: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def BrokerConnection():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        print(f'TradeBros: Broker Connection: Started')
        global broker_connection
        try:
            broker_connection.terminateSession(BROKER_USER_ID)
            sleep(5)
        except Exception as e:
            print(f'TradeBros: Broker Connection: Trying to Terminate Session Error: {e}')
        
        broker_connection = SmartConnect(api_key=BROKER_API_KEY)
        broker_connection.generateSession(BROKER_USER_ID, BROKER_PIN, totp=pyotp.TOTP(BROKER_TOTP_KEY).now())
    except Exception as e:
        print(f'TradeBros: Broker Connection: Error: {e}')
    print(f'TradeBros: Broker Connection: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def Equity_BreakOut_1(auto_trigger=True):
    product = 'equity'
    log_identifier = 'Equity_BreakOut_1'
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'TradeBros: {log_identifier}: Runtime : {product} : {now.strftime("%d-%b-%Y %H:%M:%S")}')

    try:
        global sws, open_position, broker_connection
        if auto_trigger:
            if now.time() < time(9, 18, 00):
                raise Exception(f"TradeBros: {log_identifier}: Entry Not Started")
            elif now.time() > time(15, 14, 00):
                raise Exception(f"TradeBros: {log_identifier}: Entry Not Stopped")

        configuration_obj = Configuration.objects.filter(product=product)[0]

        exclude_symbols_names = Transaction.objects.filter(product=product, indicate='EXIT', created_at__date=now.date(), is_active=True).values_list('name', flat=True)

        symbol_list_1 = Symbol.objects.filter(product=product, nifty200=True, is_active=True).exclude(name__in=exclude_symbols_names).order_by('-volume')
        symbol_list_2 = Symbol.objects.filter(product=product, midcpnifty150=True, is_active=True).exclude(name__in=exclude_symbols_names).order_by('-volume')
        symbol_list_3 = Symbol.objects.filter(product=product, smallcpnifty250=True, is_active=True).exclude(name__in=exclude_symbols_names).order_by('-volume')

        symbol_list = set(list(symbol_list_1) + list(symbol_list_2) + list(symbol_list_3))
        symbol_obj_list = {f"{sym.token}":sym for sym in symbol_list}

        print(f'TradeBros: {log_identifier}: Total Equity Symbol Picked: {len(symbol_list)}')

        symbol_details = {}
        symbol_tokens = [i.token for i in symbol_list]
        token_list = [symbol_tokens[x:x+50] for x in range(0, len(symbol_tokens), 50)]
        for list_ in token_list:
            try:
                data = broker_connection.getMarketData(mode="FULL", exchangeTokens={"NSE": list_})
                if data.get('data'):
                    fetched = data.get('data')['fetched']
                    print(f'TradeBros: {log_identifier}: Fetched: {len(symbol_details)}')
                    for i in fetched:
                        symbol_details[i['symbolToken']] = {'currentPrice': i['ltp']}
                else:
                    print(f'TradeBros: {log_identifier}: Not Fetched: {data}')
            except Exception as e:
                print(f'TradeBros: {log_identifier}: Market data Update: Loop Error: {e}')
        
        print(f'TradeBros: {log_identifier}: Total Ltp: Fetched: {len(symbol_details)}')
        new_entry = []
        for index, symbol_name in enumerate(symbol_details):
            try:
                mode = None

                # Starts
                symbol_obj = symbol_obj_list[symbol_name]
                close = symbol_details[symbol_name].get('currentPrice')
                # Ends

                entries_list = StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=True)
                if not entries_list:

                    if (symbol_obj.weekhigh52 > 0) and (symbol_obj.weekhigh52 < close):
                    # if (max_high_1y < close):
                        mode = 'CE'

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
                            'lot': symbol_obj.lot,
                            'sws': sws,
                            'open_position': open_position
                        }
                        new_entry = Price_Action_Trade(data, new_entry)
                else:
                    stock_config_obj = entries_list[0]
                    from_day = now - timedelta(days=100)
                    data_frame = historical_data(symbol_obj.token, symbol_obj.exchange, now, from_day, 'ONE_DAY', product)
                    sleep(0.3)
                    trsl_ce = min(data_frame['Low'].iloc[-50:-1]) if stock_config_obj.max < configuration_obj.target else round(close - close * (configuration_obj.trail_stoploss_by)/100, 2)

                    if stock_config_obj.mode == 'CE':
                        if not stock_config_obj.tr_hit and (stock_config_obj.stoploss < trsl_ce):
                            stock_config_obj.tr_hit = True
                            stock_config_obj.trailing_sl = trsl_ce
                            print(f'TradeBros: {log_identifier}: {index+1}: {stock_config_obj.mode} : Stoploss --> Trailing SL : {symbol_obj.symbol}')
                        elif stock_config_obj.tr_hit and (stock_config_obj.trailing_sl < trsl_ce):
                            stock_config_obj.trailing_sl = trsl_ce
                            print(f'TradeBros: {log_identifier}: {index+1}: {stock_config_obj.mode} : Old Trailing SL --> New Trailing SL : {symbol_obj.symbol}')
                    stock_config_obj.save()

            except Exception as e:
                StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=False).delete()
                print(f'TradeBros: {log_identifier}: Error: in Equity-Symbol: {symbol_obj.name} : {e}')
        del symbol_list
        print(f'TradeBros: {log_identifier}: Total New Entry {len(new_entry)} : New Entries: {new_entry}')

    except Exception as e:
        print(f'TradeBros: {log_identifier}: ERROR: Main: {e}')
    print(f'TradeBros: {log_identifier}: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def FnO_BreakOut_1(auto_trigger=True):
    sleep(1)
    product = 'future'
    log_identifier = 'FnO_BreakOut_1'
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'TradeBros: {log_identifier}: Runtime : {product} : {now.strftime("%d-%b-%Y %H:%M:%S")}')
    from_day = now - timedelta(days=90)

    try:
        if auto_trigger:
            if now.time() < time(9, 22, 00):
                raise Exception(f"TradeBros: {log_identifier}: Entry Not Started")
            elif now.time() > time(15, 11, 00):
                raise Exception(f"TradeBros: {log_identifier}: Entry Not Stopped")

        configuration_obj = Configuration.objects.filter(product=product)[0]

        today_earning = Transaction.objects.filter(product=product, indicate='EXIT', created_at__date=now.date(), is_active=True).values_list('profit', flat=True)
        
        exclude_symbols_names = Transaction.objects.filter(product=product, indicate='ENTRY', created_at__date=now.date(), is_active=True).values_list('name', flat=True)

        symbol_list = Symbol.objects.filter(product='equity', fno=True, is_active=True).order_by('-volume')

        global sws, open_position, broker_connection, entry_holder
        if not entry_holder.get(log_identifier):
            entry_holder[log_identifier] = {'Initiated': True}
            print(f'TradeBros: {log_identifier}: Entry Holder Initiated: {entry_holder.get(log_identifier)}')

        print(f'TradeBros: {log_identifier}: Total FnO Symbol Picked: {len(symbol_list)} : Entry on hold: {entry_holder[log_identifier]}')

        new_entry = []
        nop = StockConfig.objects.filter(symbol__product=product, is_active=True).count()

        index_list = [ 'NIFTY', 'BANKNIFTY', 'MIDCPNIFTY', 'FINNIFTY', 'NIFTYNXT50' ]
        for index, symbol_obj in enumerate(symbol_list):
            try:
                mode = None

                data_frame = historical_data(symbol_obj.token, symbol_obj.exchange, now, from_day, 'ONE_DAY', product)
                sleep(0.3)
                open = data_frame['Open'].iloc[-1]
                high = data_frame['High'].iloc[-1]
                low = data_frame['Low'].iloc[-1]
                close = data_frame['Close'].iloc[-1]
                prev_close = data_frame['Close'].iloc[-2]
                max_high = max(data_frame['High'].iloc[-30:-1]) if symbol_obj.name not in index_list else max(data_frame['High'].iloc[-5:-1])
                min_low = min(data_frame['Low'].iloc[-30:-1]) if symbol_obj.name not in index_list else min(data_frame['Low'].iloc[-5:-1])

                super_trend = SUPER_TREND(high=data_frame['High'], low=data_frame['Low'], close=data_frame['Close'], length=10, multiplier=3)

                entries_list = StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=True)
                if not entries_list:# and sum(today_earning) < configuration_obj.fixed_target * 2:

                    if (max_high < close) or (close > super_trend.iloc[-1] and prev_close < super_trend.iloc[-2]):
                        mode = 'CE'
                        stock_future_symbol = Symbol.objects.filter(
                                                    product='future',
                                                    name=symbol_obj.name,
                                                    symbol__endswith='CE',
                                                    strike__gt=close,
                                                    fno=True,
                                                    is_active=True).order_by('expiry', 'strike')

                    elif (min_low > close) or (close < super_trend.iloc[-1] and prev_close > super_trend.iloc[-2]):
                        mode = 'PE'
                        stock_future_symbol = Symbol.objects.filter(
                                                    product='future',
                                                    name=symbol_obj.name,
                                                    symbol__endswith='PE',
                                                    strike__lt=close,
                                                    fno=True,
                                                    is_active=True).order_by('expiry', '-strike')

                    if nop < configuration_obj.open_position and symbol_obj.name not in exclude_symbols_names and mode not in [None]:
                        data = {
                            'log_identifier': log_identifier,
                            'configuration_obj': configuration_obj,
                            'product': product,
                            'mode': mode,
                            'target': configuration_obj.target,
                            'stoploss': configuration_obj.stoploss,
                            'fixed_target': configuration_obj.fixed_target,
                            'sws': sws,
                            'open_position': open_position
                        }

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
                                nop += 1
                                break
                else:
                    stock_obj = entries_list[0]
                    # Perform action if required for Open Entries
                    if symbol_obj.name not in index_list:
                        if ((high > symbol_obj.r1 and low < symbol_obj.r1) or (high > symbol_obj.r2 and low < symbol_obj.r2) or (high > symbol_obj.pivot and low < symbol_obj.pivot) or (high > symbol_obj.s1 and low < symbol_obj.s1) or (high > symbol_obj.s2 and low < symbol_obj.s2)):
                            data = {
                                'exit_type': 'PIVOT',
                                'configuration_obj': configuration_obj,
                                'stock_obj': stock_obj
                            }
                            print(f'TradeBros: {log_identifier}: PIVOT Exit: FnO-Symbol: {symbol_obj.symbol} : {stock_obj.ltp}')
                            Stock_Square_Off(data, stock_obj.ltp)

            except Exception as e:
                StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=False).delete()
                print(f'TradeBros: {log_identifier}: Error: in FnO-Symbol: {symbol_obj.name} : {e}')
        del symbol_list
        print(f'TradeBros: {log_identifier}: Total New Entry {len(new_entry)} : New Entries: {new_entry} : Entry on hold: {entry_holder[log_identifier]}')

    except Exception as e:
        print(f'TradeBros: {log_identifier}: ERROR: Main: {e}')
    print(f'TradeBros: {log_identifier}: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def SquareOff():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'TradeBros: SQUARE OFF: Runtime : {now.strftime("%d-%b-%Y %H:%M:%S")}')
    try:
        future_configuration_obj = Configuration.objects.filter(product='future')[0]
        equity_configuration_obj = Configuration.objects.filter(product='equity')[0]

        future_entries_list = StockConfig.objects.filter(symbol__product='future', is_active=True)
        equity_intraday_entries_list = StockConfig.objects.filter(symbol__product='equity', mode='PE', is_active=True)

        entries_list = list(future_entries_list) + list(equity_intraday_entries_list)

        print(f'TradeBros: SQUARE OFF: Loop Started: Total Entries {len(entries_list)}')
        if entries_list:
            for stock_obj in entries_list:
                try:
                    if stock_obj.symbol.name not in [ 'NIFTY', 'BANKNIFTY', 'MIDCPNIFTY', 'FINNIFTY', 'NIFTYNXT50' ]:
                        data = {
                            'exit_type': 'SQ-OFF',
                            'configuration_obj': future_configuration_obj if stock_obj.symbol.product == 'future' else equity_configuration_obj,
                            'stock_obj': stock_obj
                        }
                        Stock_Square_Off(data, stock_obj.ltp)
                except Exception as e:
                    print(f'TradeBros: SQUARE OFF: Loop Error: {stock_obj.symbol.symbol} : {stock_obj.mode} : {e}')
        print(f'TradeBros: SQUARE OFF: Loop Ended')

    except Exception as e:
        print(f'TradeBros: SQUARE OFF: ERROR: Main:{e}')

    print(f'TradeBros: SQUARE OFF: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def CheckFnOSymbolDisable():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'TradeBros: CHECK FNO SYMBOL DISABLE: Runtime : {now.strftime("%d-%b-%Y %H:%M:%S")}')
    try:
        sleep(3)
        fno_entries = StockConfig.objects.filter(symbol__product='future', fno_activation=False)
        global account_connections

        print(f'TradeBros: CHECK FNO SYMBOL DISABLE: Loop Started: Total Entries {len(fno_entries)}')
        if fno_entries:
            for stock_obj in fno_entries:
                try:
                    account_entry_for_symbol = AccountStockConfig.objects.filter(symbol=stock_obj.symbol.symbol)
                    total_entry_in_accounts = account_entry_for_symbol.count()
                    not_placed_entry = 0
                    if account_entry_for_symbol:
                        for user_stock_config in account_entry_for_symbol:
                            connection = account_connections[user_stock_config.account.user_id]
                            unique_order_id = user_stock_config.order_id.split('@')[0]
                            data = connection.individual_order_details(unique_order_id)
                            if data['data']['orderstatus'] in ['rejected']:
                                AccountTransaction.objects.filter(order_id=user_stock_config.order_id).delete()
                                user_stock_config.delete()
                                not_placed_entry += 1
                        
                        if not_placed_entry == total_entry_in_accounts:
                            print(f'TradeBros: CHECK FNO SYMBOL DISABLE: Disabling the Symbol {stock_obj.symbol.symbol}')
                            StockConfig.objects.filter(symbol=stock_obj.symbol, fixed_target=stock_obj.fixed_target).delete()
                            Transaction.objects.filter(symbol=stock_obj.symbol.symbol, fixed_target=stock_obj.fixed_target).delete()
                            Symbol.objects.filter(name=stock_obj.symbol.name).update(fno=False)
                        else:
                            stock_obj.fno_activation = True
                            stock_obj.save()
                except Exception as e:
                    print(f'TradeBros: CHECK FNO SYMBOL DISABLE: Loop Error: {stock_obj.symbol.symbol} : {stock_obj.mode} : {e}')
        print(f'TradeBros: CHECK FNO SYMBOL DISABLE: Loop Ended')

    except Exception as e:
        print(f'TradeBros: CHECK FNO SYMBOL DISABLE: ERROR: Main:{e}')

    print(f'TradeBros: CHECK FNO SYMBOL DISABLE: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def PivotUpdate():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    product = 'equity'
    print(f'TradeBros: PIVOT UPDATE: Runtime : {now.strftime("%d-%b-%Y %H:%M:%S")}')
    try:
        # Set Pivot Points
        symbol_list = Symbol.objects.filter(product=product, is_active=True).order_by('-fno')

        from_day = now - timedelta(days=5)
        print(f'TradeBros: PIVOT UPDATE: Started : Total : {symbol_list.count()}')
        for index, symbol_obj in enumerate(symbol_list):
            try:
                if symbol_obj.symbol in ['Nifty 50', 'Nifty Bank', 'NIFTY MID SELECT', 'Nifty Fin Service', 'Nifty Next 50']:
                    yfsymb = {
                        'NIFTY': '^NSEI',
                        'BANKNIFTY': '^NSEBANK',
                        'MIDCPNIFTY' : 'NIFTY_MID_SELECT.NS',
                        'FINNIFTY': 'NIFTY_FIN_SERVICE.NS',
                        'NIFTYNXT50': '^NSMIDCP'
                    }
                    symbol = yfsymb[symbol_obj.name]
                else:
                    symbol = f"{symbol_obj.name}.NS"
                data_frame = yf.download(symbol, period="5d", group_by='ticker', rounding=True, progress=False)[symbol]

                last_day = data_frame.iloc[-2]

                pivot_traditional = PIVOT(last_day)
                symbol_obj.pivot = round(pivot_traditional['pivot'], 2)
                symbol_obj.r1 = round(pivot_traditional['r1'], 2)
                symbol_obj.s1 = round(pivot_traditional['s1'], 2)
                symbol_obj.r2 = round(pivot_traditional['r2'], 2)
                symbol_obj.s2 = round(pivot_traditional['s2'], 2)
                symbol_obj.r3 = round(pivot_traditional['r3'], 2)
                symbol_obj.s3 = round(pivot_traditional['s3'], 2)

                symbol_obj.save()
                # print(f'TradeBros: PIVOT UPDATE: Updated: {index+1} : {symbol_obj.name}')
            except Exception as e:
                print(f'TradeBros: PIVOT UPDATE: Loop Error: {symbol_obj.symbol} : {str(e)}')
                try:
                    data_frame = historical_data(symbol_obj.token, symbol_obj.exchange, now, from_day, 'ONE_DAY', product)
                    sleep(0.3)
                    last_day = data_frame.iloc[-2]

                    pivot_traditional = PIVOT(last_day)
                    symbol_obj.pivot = round(pivot_traditional['pivot'], 2)
                    symbol_obj.r1 = round(pivot_traditional['r1'], 2)
                    symbol_obj.s1 = round(pivot_traditional['s1'], 2)
                    symbol_obj.r2 = round(pivot_traditional['r2'], 2)
                    symbol_obj.s2 = round(pivot_traditional['s2'], 2)
                    symbol_obj.r3 = round(pivot_traditional['r3'], 2)
                    symbol_obj.s3 = round(pivot_traditional['s3'], 2)

                    symbol_obj.save()
                except Exception as e:
                    print(f'TradeBros: PIVOT UPDATE: Except Loop Error: {symbol_obj.symbol} : {str(e)}')
        print(f'TradeBros: PIVOT UPDATE: Ended')
    except Exception as e:
        print(f'TradeBros: PIVOT UPDATE: Error: {str(e)}')
    print(f'TradeBros: PIVOT UPDATE: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def CheckTodayEntry():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        entries_list = Transaction.objects.filter(product='equity', indicate='ENTRY', date__date=now.date(), is_active=True)
        users_list = AccountConfiguration.objects.filter(place_order=True, equity_enabled=True, account__is_active=True)

        print(f'TradeBros: CHECK TODAY ENTRY: Total Entry: {entries_list.count()} : Total User: {users_list.count()}')

        for instance in entries_list:
            for user_config in users_list:
                try:
                    symbol_obj = Symbol.objects.get(token=instance.token, is_active=True)
                    user_symbol_enabled_indics = [
                        (user_config.nifty50, symbol_obj.nifty50),
                        (user_config.nifty100, symbol_obj.nifty100),
                        (user_config.nifty200, symbol_obj.nifty200),
                        (user_config.midcpnifty50, symbol_obj.midcpnifty50),
                        (user_config.midcpnifty100, symbol_obj.midcpnifty100),
                        (user_config.midcpnifty150, symbol_obj.midcpnifty150),
                        (user_config.smallcpnifty50, symbol_obj.smallcpnifty50),
                        (user_config.smallcpnifty100, symbol_obj.smallcpnifty100),
                        (user_config.smallcpnifty250, symbol_obj.smallcpnifty250)
                        ]

                    # Check if any tuple contains both values as True
                    flag_user_entry = any(all(value for value in pair) for pair in user_symbol_enabled_indics)

                    if user_config.entry_amount > instance.price and flag_user_entry and not Transaction.objects.filter(
                                                product=instance.product,
                                                symbol=instance.symbol,
                                                name=instance.name,
                                                token=instance.token,
                                                exchange=instance.exchange,
                                                mode=instance.mode, indicate='EXIT', date__date=now.date(), is_active=True):
                        entry = AccountTransaction.objects.filter(
                                                        account=user_config.account,
                                                        product=instance.product,
                                                        symbol=instance.symbol,
                                                        name=instance.name,
                                                        token=instance.token,
                                                        exchange=instance.exchange,
                                                        mode=instance.mode,
                                                        indicate=instance.indicate,
                                                        type=instance.type,
                                                        price=instance.price,
                                                        target=instance.target,
                                                        fixed_target=instance.fixed_target,
                                                        stoploss=instance.stoploss)
                        if not entry:
                            # Open threads for user
                            user_thread = threading.Thread(name=f"User-{instance.symbol}-{user_config.account.first_name}", target=UserTrade, args=(True, instance, False, user_config), daemon=True)
                            user_thread.start()

                except Exception as e:
                    print(f"TradeBros: CHECK TODAY ENTRY {instance.indicate}: User Loop Error: {e}")
    except Exception as e:
        print(f'TradeBros: CHECK TODAY ENTRY: Error: {str(e)}')
    print(f'TradeBros: CHECK TODAY ENTRY: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def StopSocketSetup(log_identifier='Cron'):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'TradeBros: Stop Socket Setup : {log_identifier} : Runtime: {now.strftime("%d-%b-%Y %H:%M:%S")}')

    global sws
    try:
        sleep(2)
        sws.close_connection()
        sws = None
        print(f'TradeBros: Stop Socket Setup : {log_identifier} : Connection Closed')
        sleep(2)
    except Exception as e:
        print(f'TradeBros: Stop Socket Setup : {log_identifier} : Trying to close the connection : {e}')
    print(f'TradeBros: Stop Socket Setup : {log_identifier} : Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def SocketSetup(log_identifier='Cron'):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'TradeBros: Socket Setup : {log_identifier} : Runtime: {now.strftime("%d-%b-%Y %H:%M:%S")}')

    global broker_connection, sws, open_position
    sleep(2)

    BROKER_AUTH_TOKEN = broker_connection.access_token
    BROKER_FEED_TOKEN = broker_connection.feed_token

    new_sws = SmartWebSocketV2(BROKER_AUTH_TOKEN, BROKER_API_KEY, BROKER_USER_ID, BROKER_FEED_TOKEN)
    sleep(2)
    sws = new_sws

    correlation_id = "tradebros-socket"
    mode = 1
    nse = []
    nfo = []
    bse = []
    bfo = []
    mcx = []

    entries = StockConfig.objects.filter(is_active=True)
    for i in entries:
        open_position[i.symbol.token] = False
        if i.symbol.exchange == 'NSE':
            # nse.append(i.symbol.token)
            pass
        elif i.symbol.exchange == 'NFO':
            nfo.append(i.symbol.token)
        elif i.symbol.exchange == 'BSE':
            # bse.append(i.symbol.token)
            pass
        elif i.symbol.exchange == 'BFO':
            bfo.append(i.symbol.token)
        else:
            mcx.append(i.symbol.token)

    subscribe_list = []
    for index, i in enumerate((nse,nfo,bse,bfo,mcx)):
        if i:
            subscribe_list.append({
                "exchangeType": index+1,
                "tokens": i
            })
    print(f'TradeBros: Socket Setup : {log_identifier} : Subscribe List : {subscribe_list}')
    # if not entries:
    #     subscribe_list.append({
    #             "exchangeType": 1,
    #             "tokens": '3045'
    #         })
    
    # Streaming threads for Open Positions
    socket_thread = threading.Thread(name=f"Streaming-{now.strftime('%d-%b-%Y %H:%M:%S')}", target=connect_to_socket, args=(correlation_id, mode, subscribe_list), daemon=True)
    socket_thread.start()

    print(f'TradeBros: Socket Setup : {log_identifier} : Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def CheckLtp():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'TradeBros: Check LTP : Runtime: {now.strftime("%d-%b-%Y %H:%M:%S")}')

    global sws, open_position
    correlation_id = "tradebros-socket"
    socket_mode = 1
    try:
        symbol_obj_list = StockConfig.objects.filter(symbol__product='equity')
        symbol_list = { f"{sym.symbol.name}.NS":sym.symbol.token for sym in symbol_obj_list }
        tickers = yf.Tickers(list(symbol_list.keys())).tickers
        for ticker in tickers:
            try:
                ltp = tickers[ticker].info.get('currentPrice')
                LTP_Action(symbol_list[ticker], ltp, open_position, correlation_id, socket_mode, sws)
            except Exception as e:
                print(f'TradeBros: Check LTP : Error Loop: {ticker} : {ltp} : {e}')
    except Exception as e:
        print(f'TradeBros: Check LTP : Error Main : {e}')
    print(f'TradeBros: Check LTP : Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def TriggerBuild():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'TradeBros: TriggerBuild : Runtime: {now.strftime("%d-%b-%Y %H:%M:%S")}')
    # Fetch Services
    url = "https://api.render.com/v1/services?includePreviews=true&limit=20"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {RENDER_KEY}"
    }

    response = requests.get(url, headers=headers)

    for i in response.json():
        print(i['service']['id'])
        url = f"https://api.render.com/v1/services/{i['service']['id']}/deploys"
        payload = { "clearCache": "clear" }
        response = requests.post(url, json=payload, headers=headers)
        print(f'TradeBros: TriggerBuild : Response: ServiceName: {i["service"]["name"]} : ServiceID: {i["service"]["id"]} : {response.text}')
    print(f'TradeBros: TriggerBuild : Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True
