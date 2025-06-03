from zoneinfo import ZoneInfo
from datetime import datetime, time
from stock.models import StockConfig
from trade_bros.settings import sws, open_position
from system_conf.models import Configuration, Holiday
from helper.check_ltp import TargetExit, TrailingStopLossExit, TrailingTargetUpdate

def LTP_Action(token, ltp, open_position, correlation_id, socket_mode, sws, socket_data):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        check_holiday = Holiday.objects.filter(date=now.date(), is_active=True)
        if check_holiday:
            raise Exception(f"TradeBros: LTP ACTION: Today is Holiday : {check_holiday[0].holiday}")
        stock_obj = StockConfig.objects.filter(symbol__token=token, is_active=True)
        if stock_obj:
            stock_obj = stock_obj[0]
            if not socket_data:
                stock_obj.chart_price = ltp
                stock_obj.save()
            print(f"LTP : {now.strftime('%H:%M:%S')} : {stock_obj.symbol.symbol} : {ltp}")
            configuration_obj = Configuration.objects.filter(product=stock_obj.symbol.product)[0]
            try:
                data = {
                    'configuration_obj': configuration_obj,
                    'stock_obj': stock_obj,
                    'socket_data': socket_data
                }
                data['target'] = 3 / 100
                data['stoploss'] = configuration_obj.trail_stoploss_by / 100

                # Record Max gain hit:
                percent = round((((ltp - stock_obj.price)/stock_obj.price)) * 100, 2)
                data['percent'] = percent
                if socket_data:
                    if percent > stock_obj.max:
                        stock_obj.highest_price = round(ltp, 2)
                        stock_obj.max = round(percent, 2)
                    elif percent < stock_obj.max_l:
                        stock_obj.max_l = round(percent, 2)
                    stock_obj.ltp = ltp
                    stock_obj.save()

                if (now.time() < time(9, 15, 2)) or (now.time() > time(15, 29, 50)):
                    return True

                if stock_obj.symbol.product == 'future':
                    if (not socket_data and stock_obj.mode == 'CE' and ltp >= stock_obj.fixed_target) or (not socket_data and stock_obj.mode == 'PE' and ltp <= stock_obj.fixed_target) or (socket_data and stock_obj.capital_save and percent > configuration_obj.fixed_target):
                        TargetExit(data, ltp, open_position, correlation_id, socket_mode, sws)
                    elif not socket_data or data['percent'] < -configuration_obj.stoploss or (stock_obj.tr_hit and ltp <= stock_obj.trailing_sl):
                        TrailingStopLossExit(data, ltp, open_position, correlation_id, socket_mode, sws)
                    elif not socket_data or data['percent'] > configuration_obj.target:
                        TrailingTargetUpdate(data, ltp)
                else:
                    if ltp >= stock_obj.fixed_target:
                        TargetExit(data, ltp, open_position, correlation_id, socket_mode, sws)
                    elif not TrailingTargetUpdate(data, ltp):
                        TrailingStopLossExit(data, ltp, open_position, correlation_id, socket_mode, sws)
            except Exception as e:
                print(f'TradeBros: LTP ACTION: Loop Error: {stock_obj.symbol} : {stock_obj.mode} : {e}')
        else:
            del open_position[token]
            if stock_obj.symbol.exchange == 'NSE':
                exchangeType = 1
            elif stock_obj.symbol.exchange == 'NFO':
                exchangeType = 2
            elif stock_obj.symbol.exchange == 'BSE':
                exchangeType = 3
            elif stock_obj.symbol.exchange == 'BFO':
                exchangeType = 4
            else:
                exchangeType = 5
            # Unsubscribe Token
            sws.unsubscribe(correlation_id, socket_mode, [{"action": 0, "exchangeType": exchangeType, "tokens": [token]}])
            print(f"TradeBros: Token Removed: Unsubscribed : {token}")

    except Exception as e:
        print(f'TradeBros: LTP ACTION: ERROR: {e}')
    return True


def connect_to_socket(correlation_id, socket_mode, subscribe_list):
    try: 
        global sws, open_position

        def on_data(wsapp, message):
            ltp = message['last_traded_price']/100
            token = message['token']
            if open_position.get(token) is False:
                open_position[token] = True
                LTP_Action(token, ltp, open_position, correlation_id, socket_mode, sws, socket_data=True)
                if open_position.get(token):
                    open_position[token] = False

        def on_open(wsapp):
            print(f'TradeBros: CONNECT TO SOCKET: Opened : {subscribe_list}')
            sws.subscribe(correlation_id, socket_mode, subscribe_list)

        def on_error(wsapp, error):
            print(f'TradeBros: CONNECT TO SOCKET: Error : {error}')

        # Assign the callbacks.
        sws.on_open = on_open
        sws.on_data = on_data
        sws.on_error = on_error

        sws.connect()
    except Exception as e:
        print(f'TradeBros: CONNECT TO SOCKET: ERROR: MAIN: {e}')