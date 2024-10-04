import pyotp
import requests
from time import sleep
from zoneinfo import ZoneInfo
from SmartApi import SmartConnect
from datetime import datetime, time, timedelta
from helper.angel_function import historical_data
from stock.models import StockConfig, Transaction
from system_conf.models import Configuration, Symbol
from helper.common import calculate_volatility, last_thursday
from helper.trade_action import Price_Action_Trade, Stock_Square_Off
from helper.angel_order import Cancel_Order, Create_Order, Is_Order_Completed
from trade.settings import BED_URL_DOMAIN, BROKER_API_KEY, BROKER_PIN, BROKER_TOTP_KEY, BROKER_USER_ID, broker_connection


def stay_awake():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'Pratik: Stay Awake: Runtime: {now.strftime("%d-%b-%Y %H:%M:%S")}')
    x = requests.get(f"{BED_URL_DOMAIN}/api/trade/awake", verify=False)
    print(f'Pratik: Stay Awake: Execution Time(hh:mm:ss): {x.status_code} : {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def MarketDataUpdate():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'Pratik: Market data Update: Started : Runtime : {now.strftime("%d-%b-%Y %H:%M:%S")}')
    if now.time().minute in [0, 10, 20, 30, 40, 50]:
        sleep(5)
    nse_tokens = list(Symbol.objects.filter(exchange='NSE', is_active=True).values_list('token', flat=True))
    token_list = [nse_tokens[x:x+50] for x in range(0, len(nse_tokens), 50)]
    global broker_connection
    for list_ in token_list:
        data = broker_connection.getMarketData(mode="FULL", exchangeTokens={"NSE": list_})
        if data.get('data'):
            fetched = data.get('data')['fetched']
            for i in fetched:
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
        sleep(1)
    print(f'Pratik: Market data Update: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def SymbolSetup():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    print(f'Pratik: Symbol Setup: Started')
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    data = requests.get(url).json()

    open_entries_symbols = StockConfig.objects.filter(is_active=True).values_list('symbol__symbol', flat=True)
    Symbol.objects.filter(is_active=True).exclude(symbol__in=open_entries_symbols).delete()

    Symbol.objects.filter(expiry__lt=now.date(), is_active=True).delete()

    exclude_symbol = ['HDFCNIFTY', '031NSETEST', '151NSETEST', 'LIQUID', 'HNGSNGBEES', 'AXISCETF', 'SETFNIFBK', 'EBANKNIFTY', '171NSETEST', 'SETFNIF50', 'CPSEETF', 'GSEC10IETF', 'DIVOPPBEES', 'OILIETF', 'AUTOIETF', 'HDFCLIQUID', 'AXISNIFTY', 'NIFTY50ADD', 'CONSUMBEES', 'HDFCNIFBAN', 'NIFTYBEES', '101NSETEST', 'LIQUIDETF', 'TOP10ADD', 'NIF100BEES', 'PSUBNKIETF', 'INFRABEES', 'AXISTECETF', 'NV20BEES', 'ALPL30IETF', 'INFRAIETF', '181NSETEST', 'MOM30IETF', 'SBISILVER', 'NIFTY1', 'UTINIFTETF', 'SILVERBEES', 'BANKETFADD', 'MIDCAPIETF', 'PHARMABEES', 'SENSEXADD', 'GOLDCASE', 'HEALTHIETF', 'BSLNIFTY', 'PVTBANIETF', 'BSE500IETF', '071NSETEST', '011NSETEST', 'IVZINGOLD', 'NETF', 'SENSEXIETF', 'SBIETFIT', 'ABSLBANETF', 'SILVERTUC', 'SHARIABEES', 'EBBETF0433', 'SILVERETF', 'FMCGIETF', 'NIF10GETF', '021NSETEST', 'CONSUMIETF', 'SILVERIETF', 'SETF10GILT', 'NV20IETF', 'SDL26BEES', 'SENSEXETF', 'NIF100IETF', 'QNIFTY', 'MIDSELIETF', 'BBNPPGOLD', 'SBINEQWETF', 'NIFTYIETF', 'LIQUIDIETF', 'ITBEES', 'LICNETFSEN', '121NSETEST', '051NSETEST', 'ITETF', 'NIFTYETF', 'SILVER', 'EQUAL50ADD', 'UTISENSETF', 'QUAL30IETF', 'AXISGOLD', 'AXISHCETF', 'ALPHAETF', 'HDFCNIF100', 'PSUBNKBEES', 'BSLSENETFG', '041NSETEST', 'QGOLDHALF', 'BBETF0432', 'COMMOIETF', 'MONIFTY500', 'BBNPNBETF', 'LIQUIDCASE', 'GINNIFILA', 'GOLDIAM', 'NAVINIFTY', 'ITIETF', 'SILVER1', '131NSETEST', 'SBIETFPB', 'LICNETFN50', 'BANKBEES', 'METALIETF', 'AUTOBEES', 'ITETFADD', 'SILVERADD', 'HEALTHADD', 'GOLDSHARE', 'LIQUID1', 'AXISBPSETF', 'IVZINNIFTY', 'GILT5YBEES', '111NSETEST', 'HDFCGOLD', 'SILVRETF', 'GOLDTECH', 'BANKETF', 'LICNETFGSC', 'LTGILTBEES', 'GOLD1', 'BANKNIFTY1', '161NSETEST', 'ABSLLIQUID', 'GSEC5IETF', 'LIQUIDBETF', '061NSETEST', 'BANKIETF', 'LIQUIDSHRI', 'AXISILVER', 'UTIBANKETF', 'IDFNIFTYET', 'MIDCAPETF', 'GOLDBEES', 'FINIETF', 'EBBETF0425', 'PVTBANKADD', 'NEXT50IETF', 'ESILVER', 'GOLDETFADD', 'BANKBETF', 'JUNIORBEES', 'PSUBANKADD', 'MIDQ50ADD', 'HDFCNIFIT', 'GOLDIETF', 'EBBETF0430', 'NIF5GETF', 'BSLGOLDETF', 'EBBETF0431', 'LIQUIDSBI', 'EGOLD', 'TATAGOLD', 'TNIDETF', 'SBIETFQLTY', 'NIFITETF', 'LOWVOLIETF', 'SDL24BEES', '081NSETEST', 'GOLDETF', 'SETFGOLD', 'AXISBNKETF', 'NIFTYQLITY', 'LIQUIDADD', '141NSETEST', 'SBIETFCON', 'LIQUIDBEES', 'MID150BEES', 'SETFNN50', 'NIFMID150', '091NSETEST', 'HDFCSILVER', 'NIFTYBETF', 'LICMFGOLD', 'MOM100', 'TOP100CASE', 'MON100', 'LICNMID100', 'MIDSMALL', 'MIDCAP', 'MID150CASE', 'HDFCMID150', 'HDFCNEXT50', 'UTISXN50', 'MONQ50', 'MOM50', 'ABSLNN50ET', 'HDFCSML250', 'NEXT50', 'HDFCBSE500', 'MOSMALL250', 'UTINEXT50', 'MASPTOP50', 'HDFCSENSEX', 'AXSENSEX', '11NSETEST']

    Symbol.objects.filter(name__in=exclude_symbol, is_active=True).delete()

    last_thursday_date = last_thursday(now)
    if last_thursday_date.date() < now.date():
        month_num = now.month + 1
    else:
        month_num = now.month

    print(f'Pratik: Symbol Setup: Fetch Index Symbol List : Started')

    nifty50 = ['ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BEL', 'BPCL', 'BHARTIARTL', 'BRITANNIA', 'CIPLA', 'COALINDIA', 'DRREDDY', 'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ICICIBANK', 'ITC', 'INDUSINDBK', 'INFY', 'JSWSTEEL', 'KOTAKBANK', 'LT', 'M&M', 'MARUTI', 'NTPC', 'NESTLEIND', 'ONGC', 'POWERGRID', 'RELIANCE', 'SBILIFE', 'SHRIRAMFIN', 'SBIN', 'SUNPHARMA', 'TCS', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TECHM', 'TITAN', 'TRENT', 'ULTRACEMCO', 'WIPRO']
    
    nifty100 = ['ABB', 'ADANIENSOL', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS', 'ADANIPOWER', 'ATGL', 'AMBUJACEM', 'APOLLOHOSP', 'ASIANPAINT', 'DMART', 'AXISBANK', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BAJAJHLDNG', 'BANKBARODA', 'BEL', 'BHEL', 'BPCL', 'BHARTIARTL', 'BOSCHLTD', 'BRITANNIA', 'CANBK', 'CHOLAFIN', 'CIPLA', 'COALINDIA', 'DLF', 'DABUR', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'GAIL', 'GODREJCP', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE', 'HAVELLS', 'HEROMOTOCO', 'HINDALCO', 'HAL', 'HINDUNILVR', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'ITC', 'IOC', 'IRCTC', 'IRFC', 'INDUSINDBK', 'NAUKRI', 'INFY', 'INDIGO', 'JSWENERGY', 'JSWSTEEL', 'JINDALSTEL', 'JIOFIN', 'KOTAKBANK', 'LTIM', 'LT', 'LICI', 'LODHA', 'M&M', 'MARUTI', 'NHPC', 'NTPC', 'NESTLEIND', 'ONGC', 'PIDILITIND', 'PFC', 'POWERGRID', 'PNB', 'RECLTD', 'RELIANCE', 'SBILIFE', 'MOTHERSON', 'SHREECEM', 'SHRIRAMFIN', 'SIEMENS', 'SBIN', 'SUNPHARMA', 'TVSMOTOR', 'TCS', 'TATACONSUM', 'TATAMOTORS', 'TATAPOWER', 'TATASTEEL', 'TECHM', 'TITAN', 'TORNTPHARM', 'TRENT', 'ULTRACEMCO', 'UNIONBANK', 'UNITDSPR', 'VBL', 'VEDL', 'WIPRO', 'ZOMATO', 'ZYDUSLIFE']
    
    nifty200 = ['ABB', 'ACC', 'APLAPOLLO', 'AUBANK', 'ADANIENSOL', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS', 'ADANIPOWER', 'ATGL', 'ABCAPITAL', 'ABFRL', 'ALKEM', 'AMBUJACEM', 'APOLLOHOSP', 'APOLLOTYRE', 'ASHOKLEY', 'ASIANPAINT', 'ASTRAL', 'AUROPHARMA', 'DMART', 'AXISBANK', 'BSE', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BAJAJHLDNG', 'BALKRISIND', 'BANDHANBNK', 'BANKBARODA', 'BANKINDIA', 'MAHABANK', 'BDL', 'BEL', 'BHARATFORG', 'BHEL', 'BPCL', 'BHARTIARTL', 'BHARTIHEXA', 'BIOCON', 'BOSCHLTD', 'BRITANNIA', 'CGPOWER', 'CANBK', 'CHOLAFIN', 'CIPLA', 'COALINDIA', 'COCHINSHIP', 'COFORGE', 'COLPAL', 'CONCOR', 'CUMMINSIND', 'DLF', 'DABUR', 'DELHIVERY', 'DIVISLAB', 'DIXON', 'DRREDDY', 'EICHERMOT', 'ESCORTS', 'EXIDEIND', 'NYKAA', 'FEDERALBNK', 'FACT', 'GAIL', 'GMRINFRA', 'GODREJCP', 'GODREJPROP', 'GRASIM', 'HCLTECH', 'HDFCAMC', 'HDFCBANK', 'HDFCLIFE', 'HAVELLS', 'HEROMOTOCO', 'HINDALCO', 'HAL', 'HINDPETRO', 'HINDUNILVR', 'HINDZINC', 'HUDCO', 'ICICIBANK', 'ICICIGI', 'ICICIPRULI', 'IDBI', 'IDFCFIRSTB', 'IRB', 'ITC', 'INDIANB', 'INDHOTEL', 'IOC', 'IOB', 'IRCTC', 'IRFC', 'IREDA', 'IGL', 'INDUSTOWER', 'INDUSINDBK', 'NAUKRI', 'INFY', 'INDIGO', 'JSWENERGY', 'JSWINFRA', 'JSWSTEEL', 'JINDALSTEL', 'JIOFIN', 'JUBLFOOD', 'KPITTECH', 'KALYANKJIL', 'KOTAKBANK', 'LTF', 'LICHSGFIN', 'LTIM', 'LT', 'LICI', 'LUPIN', 'MRF', 'LODHA', 'M&MFIN', 'M&M', 'MRPL', 'MANKIND', 'MARICO', 'MARUTI', 'MFSL', 'MAXHEALTH', 'MAZDOCK', 'MPHASIS', 'MUTHOOTFIN', 'NHPC', 'NLCINDIA', 'NMDC', 'NTPC', 'NESTLEIND', 'OBEROIRLTY', 'ONGC', 'OIL', 'PAYTM', 'OFSS', 'POLICYBZR', 'PIIND', 'PAGEIND', 'PATANJALI', 'PERSISTENT', 'PETRONET', 'PHOENIXLTD', 'PIDILITIND', 'POLYCAB', 'POONAWALLA', 'PFC', 'POWERGRID', 'PRESTIGE', 'PNB', 'RECLTD', 'RVNL', 'RELIANCE', 'SBICARD', 'SBILIFE', 'SJVN', 'SRF', 'MOTHERSON', 'SHREECEM', 'SHRIRAMFIN', 'SIEMENS', 'SOLARINDS', 'SONACOMS', 'SBIN', 'SAIL', 'SUNPHARMA', 'SUNDARMFIN', 'SUPREMEIND', 'SUZLON', 'TVSMOTOR', 'TATACHEM', 'TATACOMM', 'TCS', 'TATACONSUM', 'TATAELXSI', 'TATAMOTORS', 'TATAPOWER', 'TATASTEEL', 'TATATECH', 'TECHM', 'TITAN', 'TORNTPHARM', 'TORNTPOWER', 'TRENT', 'TIINDIA', 'UPL', 'ULTRACEMCO', 'UNIONBANK', 'UNITDSPR', 'VBL', 'VEDL', 'IDEA', 'VOLTAS', 'WIPRO', 'YESBANK', 'ZOMATO', 'ZYDUSLIFE']

    midcpnifty50 = ['ACC', 'APLAPOLLO', 'AUBANK', 'ABCAPITAL', 'ALKEM', 'ASHOKLEY', 'ASTRAL', 'AUROPHARMA', 'BHARATFORG', 'CGPOWER', 'COLPAL', 'CONCOR', 'CUMMINSIND', 'DIXON', 'FEDERALBNK', 'GMRINFRA', 'GODREJPROP', 'HDFCAMC', 'HINDPETRO', 'IDFCFIRSTB', 'INDHOTEL', 'INDUSTOWER', 'KPITTECH', 'LTF', 'LUPIN', 'MRF', 'MARICO', 'MAXHEALTH', 'MPHASIS', 'MUTHOOTFIN', 'NMDC', 'OBEROIRLTY', 'OFSS', 'POLICYBZR', 'PIIND', 'PERSISTENT', 'PETRONET', 'PHOENIXLTD', 'POLYCAB', 'SBICARD', 'SRF', 'SAIL', 'SUNDARMFIN', 'SUPREMEIND', 'SUZLON', 'TATACOMM', 'UPL', 'IDEA', 'VOLTAS', 'YESBANK']
    
    midcpnifty100 = ['ACC', 'APLAPOLLO', 'AUBANK', 'ABCAPITAL', 'ABFRL', 'ALKEM', 'APOLLOTYRE', 'ASHOKLEY', 'ASTRAL', 'AUROPHARMA', 'BSE', 'BALKRISIND', 'BANDHANBNK', 'BANKINDIA', 'MAHABANK', 'BDL', 'BHARATFORG', 'BHARTIHEXA', 'BIOCON', 'CGPOWER', 'COCHINSHIP', 'COFORGE', 'COLPAL', 'CONCOR', 'CUMMINSIND', 'DELHIVERY', 'DIXON', 'ESCORTS', 'EXIDEIND', 'NYKAA', 'FEDERALBNK', 'FACT', 'GMRINFRA', 'GODREJPROP', 'HDFCAMC', 'HINDPETRO', 'HINDZINC', 'HUDCO', 'IDBI', 'IDFCFIRSTB', 'IRB', 'INDIANB', 'INDHOTEL', 'IOB', 'IREDA', 'IGL', 'INDUSTOWER', 'JSWINFRA', 'JUBLFOOD', 'KPITTECH', 'KALYANKJIL', 'LTF', 'LICHSGFIN', 'LUPIN', 'MRF', 'M&MFIN', 'MRPL', 'MANKIND', 'MARICO', 'MFSL', 'MAXHEALTH', 'MAZDOCK', 'MPHASIS', 'MUTHOOTFIN', 'NLCINDIA', 'NMDC', 'OBEROIRLTY', 'OIL', 'PAYTM', 'OFSS', 'POLICYBZR', 'PIIND', 'PAGEIND', 'PATANJALI', 'PERSISTENT', 'PETRONET', 'PHOENIXLTD', 'POLYCAB', 'POONAWALLA', 'PRESTIGE', 'RVNL', 'SBICARD', 'SJVN', 'SRF', 'SOLARINDS', 'SONACOMS', 'SAIL', 'SUNDARMFIN', 'SUPREMEIND', 'SUZLON', 'TATACHEM', 'TATACOMM', 'TATAELXSI', 'TATATECH', 'TORNTPOWER', 'TIINDIA', 'UPL', 'IDEA', 'VOLTAS', 'YESBANK']
    
    midcpnifty150 = ['3MINDIA', 'ACC', 'AIAENG', 'APLAPOLLO', 'AUBANK', 'ABBOTINDIA', 'AWL', 'ABCAPITAL', 'ABFRL', 'AJANTPHARM', 'ALKEM', 'APOLLOTYRE', 'ASHOKLEY', 'ASTRAL', 'AUROPHARMA', 'BSE', 'BALKRISIND', 'BANDHANBNK', 'BANKINDIA', 'MAHABANK', 'BAYERCROP', 'BERGEPAINT', 'BDL', 'BHARATFORG', 'BHARTIHEXA', 'BIOCON', 'CGPOWER', 'CRISIL', 'CARBORUNIV', 'COCHINSHIP', 'COFORGE', 'COLPAL', 'CONCOR', 'COROMANDEL', 'CUMMINSIND', 'DALBHARAT', 'DEEPAKNTR', 'DELHIVERY', 'DIXON', 'EMAMILTD', 'ENDURANCE', 'ESCORTS', 'EXIDEIND', 'NYKAA', 'FEDERALBNK', 'FACT', 'FORTIS', 'GMRINFRA', 'GICRE', 'GLAND', 'GLAXO', 'MEDANTA', 'GODREJIND', 'GODREJPROP', 'GRINDWELL', 'FLUOROCHEM', 'GUJGASLTD', 'HDFCAMC', 'HINDPETRO', 'HINDZINC', 'POWERINDIA', 'HONAUT', 'HUDCO', 'IDBI', 'IDFCFIRSTB', 'IRB', 'INDIANB', 'INDHOTEL', 'IOB', 'IREDA', 'IGL', 'INDUSTOWER', 'IPCALAB', 'JKCEMENT', 'JSWINFRA', 'JSL', 'JUBLFOOD', 'KPRMILL', 'KEI', 'KPITTECH', 'KALYANKJIL', 'LTF', 'LTTS', 'LICHSGFIN', 'LINDEINDIA', 'LLOYDSME', 'LUPIN', 'MRF', 'M&MFIN', 'MRPL', 'MANKIND', 'MARICO', 'MFSL', 'MAXHEALTH', 'MAZDOCK', 'METROBRAND', 'MSUMI', 'MPHASIS', 'MUTHOOTFIN', 'NLCINDIA', 'NMDC', 'NAM-INDIA', 'OBEROIRLTY', 'OIL', 'PAYTM', 'OFSS', 'POLICYBZR', 'PIIND', 'PAGEIND', 'PATANJALI', 'PERSISTENT', 'PETRONET', 'PHOENIXLTD', 'POLYCAB', 'POONAWALLA', 'PRESTIGE', 'PGHH', 'RVNL', 'SBICARD', 'SJVN', 'SKFINDIA', 'SRF', 'SCHAEFFLER', 'SOLARINDS', 'SONACOMS', 'STARHEALTH', 'SAIL', 'SUNTV', 'SUNDARMFIN', 'SUNDRMFAST', 'SUPREMEIND', 'SUZLON', 'SYNGENE', 'TATACHEM', 'TATACOMM', 'TATAELXSI', 'TATAINVEST', 'TATATECH', 'NIACL', 'THERMAX', 'TIMKEN', 'TORNTPOWER', 'TIINDIA', 'UNOMINDA', 'UPL', 'UBL', 'IDEA', 'VOLTAS', 'YESBANK', 'ZFCVINDIA']
    
    smallcpnifty50 = ['360ONE', 'AARTIIND', 'ARE&M', 'ANGELONE', 'APARINDS', 'ATUL', 'BSOFT', 'BLUESTARCO', 'BRIGADE', 'CESC', 'CASTROLIND', 'CDSL', 'CENTURYTEX', 'CAMS', 'CROMPTON', 'CYIENT', 'FINCABLES', 'GLENMARK', 'GESHIP', 'GSPL', 'HFCL', 'HINDCOPPER', 'IDFC', 'IIFL', 'INDIAMART', 'IEX', 'KPIL', 'KARURVYSYA', 'LAURUSLABS', 'MGL', 'MANAPPURAM', 'MCX', 'NATCOPHARM', 'NBCC', 'NCC', 'NH', 'NATIONALUM', 'NAVINFLUOR', 'PNBHOUSING', 'PVRINOX', 'PEL', 'PPLPHARMA', 'RBLBANK', 'RKFORGE', 'REDINGTON', 'SONATSOFTW', 'TEJASNET', 'RAMCOCEM', 'ZEEL', 'ZENSARTECH']
    
    smallcpnifty100 = ['360ONE', 'AADHARHFC', 'AARTIIND', 'AAVAS', 'ACE', 'AEGISLOG', 'AFFLE', 'ARE&M', 'AMBER', 'ANGELONE', 'APARINDS', 'ASTERDM', 'ATUL', 'BEML', 'BLS', 'BATAINDIA', 'BSOFT', 'BLUESTARCO', 'BRIGADE', 'CESC', 'CASTROLIND', 'CENTRALBK', 'CDSL', 'CENTURYTEX', 'CHAMBLFERT', 'CHENNPETRO', 'CAMS', 'CREDITACC', 'CROMPTON', 'CYIENT', 'DATAPATTNS', 'LALPATHLAB', 'FINCABLES', 'FSL', 'FIVESTAR', 'GRSE', 'GLENMARK', 'GODIGIT', 'GESHIP', 'GMDCLTD', 'GSPL', 'HBLPOWER', 'HFCL', 'HAPPSTMNDS', 'HINDCOPPER', 'IDFC', 'IFCI', 'IIFL', 'IRCON', 'ITI', 'INDIAMART', 'IEX', 'INOXWIND', 'INTELLECT', 'JBMA', 'J&KBANK', 'JWL', 'JYOTHYLAB', 'KPIL', 'KARURVYSYA', 'KAYNES', 'KEC', 'LAURUSLABS', 'MGL', 'MANAPPURAM', 'MCX', 'NATCOPHARM', 'NBCC', 'NCC', 'NSLNISP', 'NH', 'NATIONALUM', 'NAVINFLUOR', 'OLECTRA', 'PNBHOUSING', 'PVRINOX', 'PEL', 'PPLPHARMA', 'RBLBANK', 'RITES', 'RADICO', 'RKFORGE', 'RAYMOND', 'REDINGTON', 'SHYAMMETL', 'SIGNATURE', 'SONATSOFTW', 'SWSOLAR', 'SWANENERGY', 'TANLA', 'TTML', 'TEJASNET', 'RAMCOCEM', 'TITAGARH', 'TRIDENT', 'TRITURBINE', 'UCOBANK', 'WELSPUNLIV', 'ZEEL', 'ZENSARTECH']
    
    smallcpnifty250 = ['360ONE', 'AADHARHFC', 'AARTIIND', 'AAVAS', 'ACE', 'ABSLAMC', 'AEGISLOG', 'AFFLE', 'APLLTD', 'ALKYLAMINE', 'ALOKINDS', 'ARE&M', 'AMBER', 'ANANDRATHI', 'ANANTRAJ', 'ANGELONE', 'APARINDS', 'APTUS', 'ACI', 'ASAHIINDIA', 'ASTERDM', 'ASTRAZEN', 'ATUL', 'AVANTIFEED', 'BASF', 'BEML', 'BLS', 'BALAMINES', 'BALRAMCHIN', 'BATAINDIA', 'BIKAJI', 'BIRLACORPN', 'BSOFT', 'BLUEDART', 'BLUESTARCO', 'BBTC', 'BRIGADE', 'MAPMYINDIA', 'CCL', 'CESC', 'CIEINDIA', 'CAMPUS', 'CANFINHOME', 'CAPLIPOINT', 'CGCL', 'CASTROLIND', 'CEATLTD', 'CELLO', 'CENTRALBK', 'CDSL', 'CENTURYPLY', 'CENTURYTEX', 'CERA', 'CHALET', 'CHAMBLFERT', 'CHEMPLASTS', 'CHENNPETRO', 'CHOLAHLDNG', 'CUB', 'CLEAN', 'CAMS', 'CONCORDBIO', 'CRAFTSMAN', 'CREDITACC', 'CROMPTON', 'CYIENT', 'DOMS', 'DATAPATTNS', 'DEEPAKFERT', 'DEVYANI', 'LALPATHLAB', 'EIDPARRY', 'EIHOTEL', 'EASEMYTRIP', 'ELECON', 'ELGIEQUIP', 'ENGINERSIN', 'EQUITASBNK', 'ERIS', 'FINEORG', 'FINCABLES', 'FINPIPE', 'FSL', 'FIVESTAR', 'GRINFRA', 'GET&D', 'GRSE', 'GILLETTE', 'GLENMARK', 'GODIGIT', 'GPIL', 'GODFRYPHLP', 'GODREJAGRO', 'GRANULES', 'GRAPHITE', 'GESHIP', 'GAEL', 'GMDCLTD', 'GNFC', 'GPPL', 'GSFC', 'GSPL', 'HEG', 'HBLPOWER', 'HFCL', 'HAPPSTMNDS', 'HSCL', 'HINDCOPPER', 'HOMEFIRST', 'HONASA', 'ISEC', 'IDFC', 'IFCI', 'IIFL', 'INOXINDIA', 'IRCON', 'ITI', 'INDGN', 'INDIACEM', 'INDIAMART', 'IEX', 'INOXWIND', 'INTELLECT', 'JBCHEPHARM', 'JBMA', 'JKLAKSHMI', 'JKTYRE', 'JMFINANCIL', 'JPPOWER', 'J&KBANK', 'JINDALSAW', 'JUBLINGREA', 'JUBLPHARMA', 'JWL', 'JUSTDIAL', 'JYOTHYLAB', 'JYOTICNC', 'KNRCON', 'KSB', 'KAJARIACER', 'KPIL', 'KANSAINER', 'KARURVYSYA', 'KAYNES', 'KEC', 'KFINTECH', 'KIRLOSBROS', 'KIRLOSENG', 'KIMS', 'LATENTVIEW', 'LAURUSLABS', 'LEMONTREE', 'MMTC', 'MGL', 'MAHSEAMLES', 'MAHLIFE', 'MANAPPURAM', 'MASTEK', 'METROPOLIS', 'MINDACORP', 'MOTILALOFS', 'MCX', 'NATCOPHARM', 'NBCC', 'NCC', 'NSLNISP', 'NH', 'NATIONALUM', 'NAVINFLUOR', 'NETWEB', 'NETWORK18', 'NEWGEN', 'NUVAMA', 'NUVOCO', 'OLECTRA', 'PCBL', 'PNBHOUSING', 'PNCINFRA', 'PTCIL', 'PVRINOX', 'PFIZER', 'PEL', 'PPLPHARMA', 'POLYMED', 'PRAJIND', 'QUESS', 'RRKABEL', 'RBLBANK', 'RHIM', 'RITES', 'RADICO', 'RAILTEL', 'RAINBOW', 'RAJESHEXPO', 'RKFORGE', 'RCF', 'RATNAMANI', 'RTNINDIA', 'RAYMOND', 'REDINGTON', 'ROUTE', 'SBFC', 'SAMMAANCAP', 'SANOFI', 'SAPPHIRE', 'SAREGAMA', 'SCHNEIDER', 'SCI', 'RENUKA', 'SHYAMMETL', 'SIGNATURE', 'SOBHA', 'SONATSOFTW', 'SWSOLAR', 'SUMICHEM', 'SPARC', 'SUVENPHAR', 'SWANENERGY', 'SYRMA', 'TBOTEK', 'TV18BRDCST', 'TVSSCS', 'TANLA', 'TTML', 'TECHNOE', 'TEJASNET', 'RAMCOCEM', 'TITAGARH', 'TRIDENT', 'TRIVENI', 'TRITURBINE', 'UCOBANK', 'UTIAMC', 'UJJIVANSFB', 'USHAMART', 'VGUARD', 'VIPIND', 'DBREALTY', 'VTL', 'VARROC', 'MANYAVAR', 'VIJAYA', 'VINATIORGA', 'WELCORP', 'WELSPUNLIV', 'WESTLIFE', 'WHIRLPOOL', 'ZEEL', 'ZENSARTECH', 'ECLERX']

    print(f'Pratik: Symbol Setup: Fetch Index Symbol List : Ended')

    for i in data:
        product = None
        expity_date = datetime.strptime(i['expiry'], '%d%b%Y') if i['expiry'] else None
        if i['exch_seg'] in ['NSE', 'NFO'] and i['name'] not in exclude_symbol:
            if i['instrumenttype'] in ['OPTSTK'] and (expity_date.month == month_num): # , 'OPTIDX', 'OPTFUT'
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

                if i['name'] in nifty50:
                    obj.nifty50 = True
                if i['name'] in nifty100:
                    obj.nifty100 = True
                if i['name'] in nifty200:
                    obj.nifty200 = True

                if i['name'] in midcpnifty50:
                    obj.midcpnifty50 = True
                if i['name'] in midcpnifty100:
                    obj.midcpnifty100 = True
                if i['name'] in midcpnifty150:
                    obj.midcpnifty150 = True

                if i['name'] in smallcpnifty50:
                    obj.smallcpnifty50 = True
                if i['name'] in smallcpnifty100:
                    obj.smallcpnifty100 = True
                if i['name'] in smallcpnifty250:
                    obj.smallcpnifty250 = True

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

        symbol_list_1 = list(Symbol.objects.filter(product=product, smallcpnifty100=True, is_active=True).order_by('-volume'))
        symbol_list_2 = list(Symbol.objects.filter(product=product, nifty100=True, is_active=True).order_by('-volume'))
        symbol_list = symbol_list_1 + symbol_list_2

        print(f'Pratik: {log_identifier}: Total Equity Symbol Picked: {len(symbol_list)}')

        new_entry = []
        for index, symbol_obj in enumerate(symbol_list):
            try:
                nop = len(StockConfig.objects.filter(symbol__product=product, is_active=True))

                mode = None

                entries_list = StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=True)
                if not entries_list:
                    if nop < configuration_obj.open_position:
                        from_day = now - timedelta(days=400)
                        data_frame = historical_data(symbol_obj.token, symbol_obj.exchange, now, from_day, 'ONE_DAY')
                        sleep(0.3)

                        open = data_frame['Open'].iloc[-1]
                        high = data_frame['High'].iloc[-1]
                        low = data_frame['Low'].iloc[-1]
                        close = data_frame['Close'].iloc[-1]
                        max_high = max(data_frame['High'].iloc[-200:-1]) if len(data_frame) >= 202 else max(data_frame['High'].iloc[:-1])
                        min_low = min(data_frame['Low'].iloc[-200:-1]) if len(data_frame) >= 202 else min(data_frame['Low'].iloc[:-1])
                        daily_volatility = calculate_volatility(data_frame)

                        # # Calculate Pivots
                        # pivot_data_frame = data_frame
                        # pivot_data_frame.index = pd.to_datetime(pivot_data_frame['date'], format='%Y-%m-%d')
                        # logic = {'date': 'first', 'Open': 'first', 'High': 'max', 'Low':'min', 'Close': 'last', 'Volume': 'sum',}
                        # pivot_data_frame = pivot_data_frame.resample('MS').agg(logic)
                        # pivot_data_frame.reset_index(drop=True, inplace=True)

                        # pivot_candle = pivot_data_frame.iloc[-2]
                        # pivot = (pivot_candle['High'] + pivot_candle['Low'] + pivot_candle['Close'])/3
                        # R1 = 2*pivot - pivot_candle['Low']
                        # S1 = 2*pivot - pivot_candle['High']
                        # R2 = pivot + (pivot_candle['High'] - pivot_candle['Low'])
                        # S2 = pivot - (pivot_candle['High'] - pivot_candle['Low'])
                        # R3 = pivot + 2*(pivot_candle['High'] - pivot_candle['Low'])
                        # S3 = pivot - 2*(pivot_candle['High'] - pivot_candle['Low'])
    
                        if (max_high < close):# and not ((high >= R3 >= open) or (high >= R2 >= open) or (high >= R1 >= open) or (high >= pivot >= open) or (high >= S1 >= open) or (high >= S2 >= open) or (high >= S2 >= open)):
                            mode = 'CE'
    
                        # elif (min_low > close):# and not ((low <= R3 <= open) or (low <= R2 <= open) or (low <= R1 <= open) or (low <= pivot <= open) or (low <= S1 <= open) or (low <= S2 <= open) or (low <= S2 <= open)):
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
                                # 'pivot': pivot,
                                # 'R1': R1,
                                # 'R2': R2,
                                # 'R3': R3,
                                # 'S1': S1,
                                # 'S2': S2,
                                # 'S3': S3,
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
                else:
                    stock_config_obj = entries_list[0]
                    from_day = now - timedelta(days=100)
                    data_frame = historical_data(symbol_obj.token, symbol_obj.exchange, now, from_day, 'ONE_DAY')
                    sleep(0.3)

                    trsl_ce = min(data_frame['Low'].iloc[-50:-1]) if len(data_frame) >= 52 else max(data_frame['Low'].iloc[:-1])
                    trsl_pe = max(data_frame['High'].iloc[-50:-1]) if len(data_frame) >= 52 else max(data_frame['High'].iloc[:-1])

                    if stock_config_obj.mode == 'CE':
                        if not stock_config_obj.tr_hit and (stock_config_obj.stoploss < trsl_ce):
                            stock_config_obj.tr_hit = True
                            stock_config_obj.trailing_sl = trsl_ce
                            print(f'Pratik: {log_identifier}: {stock_config_obj.mode} : Stoploss --> Trailing SL : {symbol_obj.symbol}')
                        elif stock_config_obj.tr_hit and (stock_config_obj.trailing_sl < trsl_ce):
                            stock_config_obj.trailing_sl = trsl_ce
                            print(f'Pratik: {log_identifier}: {stock_config_obj.mode} : Old Trailing SL --> New Trailing SL : {symbol_obj.symbol}')
                    else:
                        if not stock_config_obj.tr_hit and (stock_config_obj.stoploss > trsl_pe):
                            stock_config_obj.tr_hit = True
                            stock_config_obj.trailing_sl = trsl_pe
                            print(f'Pratik: {log_identifier}: {stock_config_obj.mode} : Stoploss --> Trailing SL : {symbol_obj.symbol}')
                        elif stock_config_obj.tr_hit and (stock_config_obj.trailing_sl > trsl_pe):
                            stock_config_obj.trailing_sl = trsl_pe
                            print(f'Pratik: {log_identifier}: {stock_config_obj.mode} : Old Trailing SL --> New Trailing SL : {symbol_obj.symbol}')
                    stock_config_obj.save()
                del mode, entries_list

            except Exception as e:
                StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=False).delete()
                print(f'Pratik: {log_identifier}: Error: in Equity-Symbol: {symbol_obj.name} : {e}')
        del symbol_list
        print(f'Pratik: {log_identifier}: Total New Entry {len(new_entry)} : New Entries: {new_entry}')

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
            elif now.time() > time(15, 11, 00):
                raise Exception("Entry Not Stopped")

        configuration_obj = Configuration.objects.filter(product=product)[0]
        
        exclude_symbols = Transaction.objects.filter(product=product, indicate='ENTRY', created_at__date=now.date(), is_active=True).values_list('symbol', flat=True)

        exclude_symbols_names = Symbol.objects.filter(symbol__in=exclude_symbols, is_active=True).values_list('name', flat=True)

        symbol_list = Symbol.objects.filter(product='equity', fno=True, is_active=True).exclude(name__in=exclude_symbols_names).order_by('-volume')

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

                        # Calculate Pivots
                        #pivot_data_frame = data_frame
                        #pivot_data_frame.index = pd.to_datetime(pivot_data_frame['date'], format='%Y-%m-%d')
                        #logic = {'date': 'first', 'Open': 'first', 'High': 'max', 'Low':'min', 'Close': 'last', 'Volume': 'sum',}
                        #pivot_data_frame = pivot_data_frame.resample('MS').agg(logic)
                        #pivot_data_frame.reset_index(drop=True, inplace=True)

                        #pivot_candle = pivot_data_frame.iloc[-2]
                        #pivot = (pivot_candle['High'] + pivot_candle['Low'] + pivot_candle['Close'])/3
                        #R1 = 2*pivot - pivot_candle['Low']
                        #S1 = 2*pivot - pivot_candle['High']
                        #R2 = pivot + (pivot_candle['High'] - pivot_candle['Low'])
                        #S2 = pivot - (pivot_candle['High'] - pivot_candle['Low'])
                        #R3 = pivot + 2*(pivot_candle['High'] - pivot_candle['Low'])
                        #S3 = pivot - 2*(pivot_candle['High'] - pivot_candle['Low'])
    
                        if (max_high < close):# and not ((high >= R3 >= open) or (high >= R2 >= open) or (high >= R1 >= open) or (high >= pivot >= open) or (high >= S1 >= open) or (high >= S2 >= open) or (high >= S2 >= open)):
                            mode = 'CE'
                            stock_future_symbol = Symbol.objects.filter(
                                                        product='future',
                                                        name=symbol_obj.name,
                                                        symbol__endswith='CE',
                                                        strike__gt=close,
                                                        fno=True,
                                                        is_active=True).order_by('strike')
    
                        elif (min_low > close):# and not ((low <= R3 <= open) or (low <= R2 <= open) or (low <= R1 <= open) or (low <= pivot <= open) or (low <= S1 <= open) or (low <= S2 <= open) or (low <= S2 <= open)):
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
                                'fixed_target': configuration_obj.fixed_target,
                                # 'pivot': pivot,
                                # 'R1': R1,
                                # 'R2': R2,
                                # 'R3': R3,
                                # 'S1': S1,
                                # 'S2': S2,
                                # 'S3': S3,
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
                else:
                    stock_config_obj = entries_list[0]
                    # Place Stoploss Limit Order
                    if configuration_obj.place_order and not stock_config_obj.stoploss_order_placed and Is_Order_Completed(stock_config_obj.order_id):
                        order_id, order_status, price = Create_Order(configuration_obj, 'sell', 'CARRYFORWARD', stock_config_obj.symbol.token, stock_config_obj.symbol.symbol, stock_config_obj.symbol.exchange, stock_config_obj.stoploss, stock_config_obj.lot, "LIMIT")
                        stock_config_obj.stoploss_order_placed = True
                        stock_config_obj.stoploss_order_id = order_id

                    # Place Target Limit Order
                    # if configuration_obj.place_order and not stock_config_obj.target_order_placed and Is_Order_Completed(stock_config_obj.order_id):
                    #     order_id, order_status, price = Create_Order(configuration_obj, 'sell', 'CARRYFORWARD', stock_config_obj.symbol.token, stock_config_obj.symbol.symbol, stock_config_obj.symbol.exchange, stock_config_obj.fixed_target, stock_config_obj.lot, "LIMIT")
                    #     stock_config_obj.target_order_placed = True
                    #     stock_config_obj.target_order_id = order_id
                    stock_config_obj.save()

                del mode, entries_list

            except Exception as e:
                StockConfig.objects.filter(symbol__product=product, symbol__name=symbol_obj.name, is_active=False).delete()
                print(f'Pratik: {log_identifier}: Error: in FnO-Symbol: {symbol_obj.name} : {e}')
        del symbol_list
        print(f'Pratik: {log_identifier}: Total New Entry {len(new_entry)} : New Entries: {new_entry}')

    except Exception as e:
        print(f'Pratik: {log_identifier}: ERROR: Main: {e}')
    print(f'Pratik: {log_identifier}: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def SquareOff():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    product = 'future'
    print(f'Pratik: SQUARE OFF: Runtime : {product} : {now.strftime("%d-%b-%Y %H:%M:%S")}')

    try:
        configuration_obj = Configuration.objects.filter(product=product)[0]

        entries_list = StockConfig.objects.filter(symbol__product=product, is_active=True)

        print(f'Pratik: SQUARE OFF: Loop Started: Total Entries {len(entries_list)}')
        if entries_list:
            for stock_obj in entries_list:
                try:
                    data = {
                        'configuration_obj': configuration_obj,
                        'stock_obj': stock_obj
                    }
                    if configuration_obj.place_order and not Is_Order_Completed(stock_obj.order_id):
                        print(f"Pratik: SQUARE OFF: Cancel Buy Order : {stock_obj.symbol.symbol} : {stock_obj.symbol.token}")
                        cancel_id, error_status = Cancel_Order(stock_obj.order_id)
                        if stock_obj.stoploss_order_placed:
                            cancel_id, error_status = Cancel_Order(stock_obj.stoploss_order_id)
                        if stock_obj.target_order_placed:
                            cancel_id, error_status = Cancel_Order(stock_obj.target_order_id)
                        Transaction.objects.filter(order_id=stock_obj.order_id, is_active=True).delete()
                    else:
                        Stock_Square_Off(data, stock_obj.ltp)
                except Exception as e:
                    print(f'Pratik: SQUARE OFF: Loop Error: {stock_obj.symbol.symbol} : {stock_obj.mode} : {e}')
        print(f'Pratik: SQUARE OFF: Loop Ended')

    except Exception as e:
        print(f'Pratik: SQUARE OFF: ERROR: Main:{e}')

    print(f'Pratik: SQUARE OFF: Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True
