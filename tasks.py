import json
import requests
from time import sleep

from django.db.models import Count, Sum
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from helper.angel_orders import Create_Order
from helper.trade_action import ForceExit, Price_Action_Trade
from logs.logger import create_logger, write_error_log, write_info_log
from logs.models import Log
from option.models import DailyRecord, OptionSymbol, StockConfig, Transaction, Index
from helper.fyer_auto_generate_key import GenerateFyersToken
from helper.check_ltp import TargetExit, TrailingStopLossExit, TrailingTargetUpdate, SquareOff
from helper.common import Check_Entry, next_expiry_date, Entry_Call, Entry_Put
from helper.connection import AngelOne, Fyers
from helper.get_data import fyers_get_data
from helper.indicator import PIVOT, SUPER_TREND
from helper.option_setup import GetVelocity, StockConfigs
from system_conf.models import Configuration
from trade_bros.settings import BED_URL_DOMAIN


def RecordUpdate():
    if datetime.now(tz=ZoneInfo("Asia/Kolkata")).weekday() == 3:
        return True
    # Record Daily Overall P/L% with total entries
    configuration_obj = Configuration.objects.filter(is_active=True)[0]
    DailyRecord.objects.create(
        date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(),
        day=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date().strftime("%A"),
        total_entry=len(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT')),
        p_l=round(sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT').values_list('profit', flat=True))
        , 2),
        daily_max_profit=configuration_obj.daily_max_profit,
        daily_max_profit_time=configuration_obj.daily_max_profit_time,
        daily_max_loss=configuration_obj.daily_max_loss,
        daily_max_loss_time=configuration_obj.daily_max_loss_time)
    return True


def Daily_P_L_Update():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    configuration_obj = Configuration.objects.filter(is_active=True)[0]
    transaction_list = Transaction.objects.filter(indicate='EXIT', date__date=now.date()).order_by('date')
    w_p_l = 0
    p_l = 0
    configuration_obj.daily_max_profit = 0
    configuration_obj.daily_max_loss = 0
    for t_obj in transaction_list:
        w_p_l += t_obj.profit
        if t_obj.date.date() == datetime.now(tz=ZoneInfo("Asia/Kolkata")).date():
            p_l += t_obj.profit
            if p_l > configuration_obj.daily_max_profit:
                configuration_obj.daily_max_profit = round(p_l, 2)
                configuration_obj.daily_max_profit_time = t_obj.date
            elif p_l < configuration_obj.daily_max_loss:
                configuration_obj.daily_max_loss = round(p_l, 2)
                configuration_obj.daily_max_loss_time = t_obj.date
    configuration_obj.save()
    return True


def DeleteLogs():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        Log.objects.filter(created_at__date__lte=now).delete()
        if now.time() > time(15, 30, 00) or now.time() < time(9, 00, 00):
            Configuration.objects.filter(is_active=True).update(daily_max_profit=0, daily_max_loss=0)
    except Exception as e:
        print(f'Error: {str(e)}')
    return True


def NotifyUsers():
    # create or get log in db
    logger = create_logger(
        file_name=f'Notify_User_{datetime.now(tz=ZoneInfo("Asia/Kolkata")).date()}')
    write_info_log(logger, 'Notify User: Started')
    
    try:
        now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
        phone_number_id = "139249165928488" # Phone number ID provided
        access_token = "EAAPJg0jr5E0BOwSOFZAVl9kN4CvvRPa23NBUMyUIKZBC9msakFSWqmZAMLJYEP3KGDzAYDo6dCiQrGj9I2HV4nW2BnZALuBZCwbhVeZCq8N85dszDHnpJC7XZCah51lTmXJcbvHwXXnThvb7yE15je8JTcTDhXRZB1WbnOhZCJkZAsafZCBLZAJSAJaO9XruWlRoY1uN" # Your temporary access token

        day_date = f'{now.strftime("%A, %d %B, %Y")}, Trade-Bros'
        price_action_obj = DailyRecord.objects.get(date=now.date(), is_active=True)

        price_action_str = ""
        total_str = ""
        price_action_str += 'Sataru-Gojo: ' + '*' + str(price_action_obj.p_l) + ' %' + '*' + ' on: ' + '*' + str(price_action_obj.total_entry) + '*' + ' trade, were we reached a Max-Profit of ' + '*' + str(price_action_obj.daily_max_profit) + ' %' + '*'  +  ' with Max-Loss of ' + '*' + str(price_action_obj.daily_max_loss) + ' %' + '*' + '.'

        total_str = 'Total: ' + '*' + str(price_action_obj.p_l) + ' %' + '*' + ' on ' + '*' + str(price_action_obj.total_entry) + '*' + ' trades. '
        
        transaction_list = Transaction.objects.filter(date__date = datetime.now().date(), indicate='EXIT', is_active=True).values('index').annotate(profit=Sum('profit'), trade=Count('indicate'))
        index_wise_str = ''
        for trans_obj in transaction_list:
            index_wise_str += trans_obj['index'] + ": " + '*' + str(round(trans_obj['profit'])) + '%' + '*' + ' : on ' + '*' + str(trans_obj['trade']) + '*' + " trades. "
        index_wise_str += '-----------------'

        if price_action_str == '':
            price_action_str = 'Sataru Gojo : *No Trade*'
        if index_wise_str == '':
            index_wise_str = '*No Trade*'
        if total_str == '':
            total_str = '*No Trade*'
        else:
            daily_sl_obj = Configuration.objects.all()[0]
            today_earning = round(daily_sl_obj.amount*price_action_obj.p_l/100)
            earning = 'Profit' if today_earning > 0 else 'Loss'
            total_str += '-----------------------------------'
            total_str +=  f"Today's {earning} will be approx: " + '*' + f"{today_earning}" + '*' + " /- on per trade of approx amount: " + '*' + f"{daily_sl_obj.amount}" + '*' + '/-. '

            if (sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT').values_list('profit', flat=True)) < -daily_sl_obj.daily_fixed_stoploss):
                total_str += '-----------------------------------'
                total_str +=  '*' + f'Trading Stopped because Daily Stoploss Hitted {daily_sl_obj.daily_fixed_stoploss} % at {(daily_sl_obj.daily_max_loss_time + timedelta(hours=5, minutes=30)).strftime("%T")}' + '*' + '.'

        recipient_phone_number_list = [("Pratik", "+917000681073"), ("Sudeep", '+919713113031'), ("Himanshu", '+917415535562'), ]

        for user_name, recipient_phone_number in recipient_phone_number_list:
            sleep(1)
            url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {access_token}",
                'Content-Type': 'application/json'
            }

            msg_header_params = [
                {
                    "type": "text",
                    "text": user_name
                }
            ]
            msg_body_params = [
                    {
                        "type": "text",
                        "text": day_date
                    },
                    {
                        "type": "text",
                        # "text": motivation_quote
                        "text": price_action_str
                    },
                    {
                        "type": "text",
                        "text": index_wise_str
                    },
                    {
                        "type": "text",
                        "text": total_str
                    }
            ]
            data = {
                'messaging_product': 'whatsapp',
                'to': recipient_phone_number,
                'type': 'template',
                'template': {
                    'name': 'trade_bros_daily_trade_notification',
                    'language': {
                        'code': 'en'
                    },
                    'components': [
                        {
                            'type': 'header',
                            'parameters': msg_header_params
                        },
                        {
                            'type': 'body',
                            'parameters': msg_body_params
                        }
                            
                    ]
                }
            }

            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                write_info_log(
                    logger, f"Successfully Notified to {user_name}: {recipient_phone_number}.")
            write_info_log(
                    logger, f"Response: {response.content}.")
    except Exception as e:
        write_error_log(logger, f'{e}')
    write_info_log(logger, f'Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def FyersSetup():
    # create or get log in db
    logger = create_logger(
        file_name=f'FyersSetup_{datetime.now(tz=ZoneInfo("Asia/Kolkata")).date()}')
    write_info_log(logger, 'FyersSetup: Started')

    try:
        sleep(3)
        global angel_pratik_conn
        angel_pratik_conn, _ = AngelOne('Angel-Himanshu')
        user_profile_name = GenerateFyersToken('Fyers-Pratik')
        write_info_log(
            logger, f"Fyer's User Profile name is {user_profile_name}.")

    except Exception as e:
        write_error_log(logger, f'{e}')

    write_info_log(logger, 'FyersSetup: Ended')
    return True


def StayAwake():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    # create or get log in db
    # logger = create_logger(
    #    file_name=f'awake-{datetime.now(tz=ZoneInfo("Asia/Kolkata")).date()}')
    # write_info_log(logger, f"Calling URL: {BED_URL_DOMAIN}/api/trade/awake")
    x = requests.get(f"{BED_URL_DOMAIN}/api/trade/awake", verify=False)
    # write_info_log(logger, f'SCHE: Time: {datetime.now(tz=ZoneInfo("Asia/Kolkata")).strftime("%d-%b-%Y %H:%M:%S")}, Status: {x.status_code}')
    # write_info_log(logger, f'Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    return True


def PivotUpdate():
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))

    # create or get log in db
    logger = create_logger(
        file_name=f'Pivot_{now.date()}')

    write_info_log(logger, 'Pivot: STARTED')
    try:
        # Set Pivot Points
        fyers_conn = Fyers('Fyers-Pratik')
        index_obj_list = Index.objects.filter(is_active=True).order_by('expiry_date')

        from_day = now - timedelta(days=10)
        write_info_log(logger, f'Pivot: Started')
        for index_obj in index_obj_list:
            if now.date() == index_obj.expiry_date:
                index_obj.trailing_target = True
            else:
                index_obj.trailing_target = False
            data_frame = fyers_get_data(
                index_obj.index_symbol , now, from_day, 'D', fyers_conn, logger=logger)
            sleep(0.2)

            # last_day = data_frame.iloc[-1] if data_frame['date'].iloc[-1].date() == now.date() else data_frame.iloc[-2]
            last_day = data_frame.iloc[-2]

            pivot_traditional = PIVOT(last_day)
            index_obj.pivot = round(pivot_traditional['pivot'], 2)
            index_obj.r1 = round(pivot_traditional['r1'], 2)
            index_obj.s1 = round(pivot_traditional['s1'], 2)
            index_obj.r2 = round(pivot_traditional['r2'], 2)
            index_obj.s2 = round(pivot_traditional['s2'], 2)
            index_obj.r3 = round(pivot_traditional['r3'], 2)
            index_obj.s3 = round(pivot_traditional['s3'], 2)

            index_obj.save()
            write_info_log(logger, f'Updated: {index_obj}')

        write_info_log(logger, f'Pivot: Ended')
    except Exception as e:
        write_error_log(logger, f'Error: {str(e)}')
    write_info_log(
        logger, f'Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    write_info_log(logger, 'Pivot: ENDED')
    return True


def BasicSetupJob():
    # create or get log in db
    logger = create_logger(
        file_name=f'BasicSetup_{datetime.now(tz=ZoneInfo("Asia/Kolkata")).date()}')
    write_info_log(logger, 'BasicSetup: Started')

    try:
        # Fetch Data
        data = {
            # "BANKEX": ["BSE:BANKEX-INDEX", next_expiry_date(datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), 0).strftime('%d-%b-%Y'), 100, 1, '99919012'],
            "MIDCPNIFTY": ["NSE:MIDCPNIFTY-INDEX", next_expiry_date(datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), 0).strftime('%d-%b-%Y'), 25, 1, '99926014'],
            "FINNIFTY": ["NSE:FINNIFTY-INDEX", next_expiry_date(datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), 1).strftime('%d-%b-%Y'), 50, 2, '99926037'],
            "BANKNIFTY": ["NSE:NIFTYBANK-INDEX", next_expiry_date(datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), 2).strftime('%d-%b-%Y'), 100, 3, '99926009'],
            "NIFTY": ["NSE:NIFTY50-INDEX", next_expiry_date(datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), 3).strftime('%d-%b-%Y'), 50, 4, '99926000'],
            "SENSEX": ["BSE:SENSEX-INDEX", next_expiry_date(datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), 4).strftime('%d-%b-%Y'), 100, 5, '99919000'],
        }

        # Stocks Setup
        StockConfigs(data, logger)

        # Initiate Connection
        conn = Fyers('Fyers-Pratik')

        # Calculate Velocity
        OptionSymbol.objects.all().delete()
        GetVelocity(data=data, conn=conn, logger=logger)

    
        # Amount Update on friday
        if datetime.now(tz=ZoneInfo("Asia/Kolkata")).weekday() == 4:
            to_date = datetime.now(tz=ZoneInfo("Asia/Kolkata")).date()
            from_date = to_date - timedelta(days=6)
            weekly_sum = sum(DailyRecord.objects.filter(
                date__gte=from_date,
                date__lte=to_date,
                is_active=True).values_list('p_l', flat=True))
            system_conf_obj = Configuration.objects.filter(is_active=True)[0]

            system_conf_obj.amount = system_conf_obj.amount + system_conf_obj.amount * ( 0.1 ) if weekly_sum > 10 else system_conf_obj.amount - system_conf_obj.amount * ( 0.1 )
            system_conf_obj
            system_conf_obj.save()

    except Exception as e:
        write_error_log(logger, f'{e}')

    write_info_log(logger, 'BasicSetup: Ended')
    return True


def Minute1():
    try:
        sleep(1)
        now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))

        # create or get log in db
        logger = create_logger(
            file_name=f'{now.strftime("%d-%b-%Y %H:%M:%S")}-Minute_1')
        write_info_log(logger, 'Minute_1: Started')

        if now.weekday() == 3:
            raise Exception("Trading not allowed on Thursdays")

        if now.time() < time(9, 18, 00):
            raise Exception("Market Not Started")
        elif now.time() > time(15, 14, 00):
            raise Exception("Market is Closed")

        fyers_conn = Fyers('Fyers-Pratik')
        global angel_pratik_conn
        angel_conn = angel_pratik_conn

        configuration_obj = Configuration.objects.filter(is_active=True)[0]

        index_obj_list = Index.objects.filter(is_active=True).order_by('expiry_date')

        for index_obj in index_obj_list:
            try:
                write_info_log(logger, f'Index: {index_obj.index} : Started')

                symbol_list = []
                mode = None

                days_difference = (index_obj.expiry_date - now.date()).days
                entries_list = StockConfig.objects.filter(symbol__index=index_obj, is_active=True)

                if not entries_list:
                    if Check_Entry(now, configuration_obj, index_obj, days_difference):
                        write_info_log(logger, f'Index: {index_obj.index} : Entry Passed')
                        pass
                    else:
                        from_day = now - timedelta(days=7)
                        data_frame = fyers_get_data(
                            index_obj.index_symbol , now, from_day, '1', fyers_conn, logger=logger)

                        underlying_ltp = data_frame['Close'].iloc[-1]
                        write_info_log(logger, f'{index_obj.index} LTP : {underlying_ltp}')

                        if Entry_Call(data_frame, index_obj):
                            data_frame_5 = fyers_get_data(
                                index_obj.index_symbol , now, from_day, '5', fyers_conn, logger=logger)

                            super_trend = SUPER_TREND(high=data_frame_5['High'], low=data_frame_5['Low'], close=data_frame_5['Close'], length=10, multiplier=3)

                            if data_frame_5['Close'].iloc[-1] > super_trend[-1]:
                                put_entry_stock_obj_list = StockConfig.objects.filter(mode='PE', symbol__index=index_obj)
                                ForceExit(put_entry_stock_obj_list, fyers_conn, angel_conn, configuration_obj)
                                put_entry_stock_obj_list.delete()
                                mode = 'CE'
                                symbol_list = [ f"{symbol}{mode}" for symbol in OptionSymbol.objects.filter(index=index_obj,  strike_price__gte=underlying_ltp, is_active=True).values_list('symbol', flat=True) ]
                                symbol_list.sort()
                                write_info_log(logger, f"{mode}-Entry:")
                        elif Entry_Put(data_frame, index_obj):
                            data_frame_5 = fyers_get_data(
                                index_obj.index_symbol , now, from_day, '5', fyers_conn, logger=logger)
                            
                            super_trend = SUPER_TREND(high=data_frame_5['High'], low=data_frame_5['Low'], close=data_frame_5['Close'], length=10, multiplier=3)

                            if data_frame_5['Close'].iloc[-1] < super_trend[-1]:
                                call_entry_stock_obj_list = StockConfig.objects.filter(mode='CE', symbol__index=index_obj)
                                ForceExit(call_entry_stock_obj_list, fyers_conn, angel_conn, configuration_obj)
                                call_entry_stock_obj_list.delete()
                                mode = 'PE'
                                symbol_list = [ f"{symbol}{mode}" for symbol in OptionSymbol.objects.filter(index=index_obj,strike_price__lte=underlying_ltp, is_active=True).values_list('symbol', flat=True) ]
                                symbol_list.sort(reverse=True)
                                write_info_log(logger, f"{mode}-Entry:")

                        else:
                            mode = None

                        if days_difference == 0:
                            if index_obj.index in ['NIFTY']:
                                fix_target = index_obj.fixed_target - 10
                            else:
                                fix_target = index_obj.fixed_target
                        elif index_obj.index in ['FINNIFTY', 'BANKNIFTY'] and days_difference in [6, 5]:
                            fix_target = 13.33
                        elif days_difference in [1, 2, 3]:
                            fix_target = 13.33
                        else:
                            fix_target = index_obj.fixed_target/days_difference
                        data = {
                            'mode': mode,
                            'index': index_obj,
                            'configuration': configuration_obj,
                            'target': index_obj.target,
                            'stoploss': index_obj.stoploss,
                            'logger': logger,
                            'fixed_target': fix_target,
                            'conn': fyers_conn,
                            'angel_conn': angel_conn,
                        }

                        for symbol in symbol_list:
                            try:
                                ltp = fyers_conn.quotes({"symbols": symbol})['d'][0]['v']['lp']
                                data['symbol'] = symbol
                                data['price'] = ltp
                                if ltp > index_obj.min_price:
                                    if ltp < index_obj.max_price:
                                        write_info_log(logger, f"{data['symbol']} on price {ltp} : Volatility : {data['fixed_target']}")
                                        Price_Action_Trade(data)
                                        break
                                else:
                                    break
                            except Exception as e:
                                write_error_log(logger, f'Trade Loop: {symbol}: {e}')

                else:
                    from_day = now - timedelta(days=7)
                    data_frame = fyers_get_data(
                        index_obj.index_symbol , now, from_day, '1', fyers_conn, logger=logger)
                    write_info_log(logger, f'{index_obj.index} : 1 Min Check : Days Diff: {days_difference}')

                    super_trend = SUPER_TREND(high=data_frame['High'], low=data_frame['Low'], close=data_frame['Close'], length=10, multiplier=3)

                    underlying_ltp = data_frame['Close'].iloc[-1]
                    write_info_log(logger, f'{index_obj.index} LTP : {underlying_ltp}')
                    write_info_log(logger, f"High : {data_frame['High'].iloc[-1]} : Close : {data_frame['Close'].iloc[-1]} : Low : {data_frame['Low'].iloc[-1]}")

                    for stock_obj in entries_list:
                        if stock_obj.mode == 'CE':
                            if data_frame['Low'].iloc[-1] < super_trend[-1]:
                                write_info_log(logger, f"Force-Exit : {stock_obj.mode} : {stock_obj.symbol}")
                                ForceExit([stock_obj], fyers_conn, angel_conn, configuration_obj)
                                stock_obj.delete()
                                pass
                        elif stock_obj.mode == 'PE':
                            if data_frame['High'].iloc[-1] > super_trend[-1]:
                                write_info_log(logger, f"Force-Exit : {stock_obj.mode} : {stock_obj.symbol}")
                                ForceExit([stock_obj], fyers_conn, angel_conn, configuration_obj)
                                stock_obj.delete()
                                pass
                        else:
                            write_info_log(logger, f"Mode not available : {stock_obj.mode} : {stock_obj.symbol}")

                write_info_log(logger, f'Index: {index_obj.index} : Ended')
            except Exception as e:
                write_error_log(logger, f'Error in Index: {index_obj.index} : {e}')

    except Exception as e:
        write_error_log(logger, f'{e}')

    write_info_log(
        logger, f'Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    write_info_log(logger, 'Minute_1: Ended')
    return True


def CallPutAction():
    try:
        now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))

        # create or get log in db
        logger = create_logger(
            file_name=f'{now.strftime("%d-%b-%Y %H:%M:%S")}-Call-Put-Action')
        write_info_log(logger, 'Call Put Action: Started')

        if now.time() < time(9, 15, 1):
            raise Exception("Market Not Started")
        elif now.time() > time(15, 17, 00):
            raise Exception("Square Off Stopped")
        elif now.time() > time(15, 29, 00):
            raise Exception("Market is Closed")
        elif (now.time().second in [57, 58, 59, 0, 1, 2, 3, 4, 5]):
            write_info_log(logger, f"LTP: 0th Second.")
            return True

        entries_list = StockConfig.objects.filter(is_active=True)

        configuration_obj = Configuration.objects.filter(is_active=True)[0]
        if entries_list:
            global angel_pratik_conn
            angel_conn = angel_pratik_conn
            data = {
                'conn': angel_conn
            }
            write_info_log(logger, f'Entries Loop Started: Total Entries {len(entries_list)}')
            for stock_obj in entries_list:
                try:
                    if configuration_obj.place_order and stock_obj.order_id in ['0', 0]:
                        order_id, order_status, price = Create_Order(configuration_obj, stock_obj, stock_obj.price, angel_conn)
                        stock_obj.order_id = order_id
                        stock_obj.order_status = order_status
                        stock_obj.save()

                        Transaction.objects.filter(date__date=now.date(), index=stock_obj.symbol.index, mode=stock_obj.mode, indicate='ENTRY', type='BUY', price=stock_obj.price, fixed_target=stock_obj.fixed_target).update(order_id=order_id, order_status=order_status)

                        write_info_log(logger, f'Buy Order Placed: {order_id} : {stock_obj.symbol} : {stock_obj.mode}')
                        return True

                    data['stock_obj'] = stock_obj
                    data['configuration'] = configuration_obj
                    data['symbol'] = f"{stock_obj.symbol.symbol}{stock_obj.mode}"
                    data['logger'] = logger
                    if stock_obj.mode == 'CE':
                        symbol = stock_obj.symbol.call_angel_symbol
                        token = stock_obj.symbol.call_token
                    else:
                        symbol = stock_obj.symbol.put_angel_symbol
                        token = stock_obj.symbol.put_token
                    data['target'] = 1 / 100
                    data['stoploss'] = 7 / 100

                    if stock_obj.symbol.symbol[:3] == 'BSE':
                        exchange_seg = 'BFO'
                    else:
                        exchange_seg = 'NFO'

                    ltp1 = angel_conn.ltpData(exchange_seg, symbol, token)
                    ltp = ltp1['data']['ltp']
                    sleep(0.2)
                    write_info_log(logger, f"LTP: {stock_obj.mode} : {symbol} : {ltp} : {token}")

                    # Record Max gain hit:
                    percent = (((ltp - stock_obj.price)/stock_obj.price)) * 100
                    data['percent'] = percent
                    if percent > stock_obj.max:
                        stock_obj.highest_price = round(ltp, 2)
                        stock_obj.max = round(percent, 2)
                    elif percent < stock_obj.max_l:
                        stock_obj.max_l = round(percent, 2)
                    stock_obj.curr_price = ltp
                    if datetime.now(tz=ZoneInfo("Asia/Kolkata")).time().second not in [0, 1, 2, 3, 4, 5]:
                        stock_obj.save()

                    if time(15, 15, 00) <= now.time():
                        SquareOff(data, ltp)
                    elif (ltp > stock_obj.fixed_target) or (not stock_obj.symbol.index.trailing_target):
                        TargetExit(data, ltp)
                        TrailingStopLossExit(data, ltp)
                    elif not TrailingTargetUpdate(data, ltp):
                        TrailingStopLossExit(data, ltp)
                except Exception as e:
                    write_error_log(logger, f'Loop Error: {stock_obj.symbol.symbol} : {stock_obj.mode} : {e}')
            write_info_log(logger, 'Entries Loop Ended')

    except Exception as e:
        write_error_log(logger, f'{e}')

    write_info_log(
        logger, f'Execution Time(hh:mm:ss): {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
    write_info_log(logger, 'Call Put Action: Ended')
    return True
