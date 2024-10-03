from zoneinfo import ZoneInfo
from datetime import datetime, time
from system_conf.models import Configuration
from trade.settings import sws, open_position
from stock.models import StockConfig, Transaction
from helper.angel_order import Is_Order_Completed, Cancel_Order
from helper.check_ltp import TargetExit, TrailingStopLossExit, TrailingTargetUpdate

def LTP_Action(token, ltp, open_position, correlation_id, socket_mode, sws):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        if now.time() < time(9, 15, 2):
            print("Market Not Started")
            return True
        elif now.time() > time(15, 29, 50):
            print("Market Closed")
            return True

        stock_obj = StockConfig.objects.filter(symbol__token=token, is_active=True)
        if stock_obj:
            stock_obj = stock_obj[0]
            configuration_obj = Configuration.objects.filter(product=stock_obj.symbol.product)[0]
            try:
                data = {
                    'configuration_obj': configuration_obj,
                    'stock_obj': stock_obj
                }
                data['target'] = 1 / 100
                data['stoploss'] = configuration_obj.trail_stoploss_by / 100

                # Record Max gain hit:
                percent = round((((ltp - stock_obj.price)/stock_obj.price)) * 100, 2)
                data['percent'] = percent
                if percent > stock_obj.max:
                    stock_obj.highest_price = round(ltp, 2)
                    stock_obj.max = round(percent, 2)
                elif percent < stock_obj.max_l:
                    stock_obj.max_l = round(percent, 2)
                stock_obj.ltp = ltp
                stock_obj.save()

                if ltp >= stock_obj.fixed_target:
                    if configuration_obj.place_order and not Is_Order_Completed(stock_obj.order_id):
                        cancel_id, error_status = Cancel_Order(stock_obj.order_id)
                        if stock_obj.stoploss_order_placed:
                            cancel_id, error_status = Cancel_Order(stock_obj.stoploss_order_id)
                        if stock_obj.target_order_placed:
                            cancel_id, error_status = Cancel_Order(stock_obj.target_order_id)
                        Transaction.objects.filter(order_id=stock_obj.order_id, is_active=True).delete()

                        # Unsubscribe Token
                        sws.unsubscribe(correlation_id, socket_mode, [{"action": 0, "exchangeType": 1, "tokens": [stock_obj.symbol.token]}])
                        print(f"Pratik: Cancelled: Unsubscribed : {stock_obj.symbol.symbol} : {stock_obj.symbol.token}")
                        stock_obj.delete()
                        return True
                    TargetExit(data, ltp, open_position, correlation_id, socket_mode, sws)
                elif not TrailingTargetUpdate(data, ltp):
                    if configuration_obj.place_order and not Is_Order_Completed(stock_obj.order_id):
                        cancel_id, error_status = Cancel_Order(stock_obj.order_id)
                        if stock_obj.stoploss_order_placed:
                            cancel_id, error_status = Cancel_Order(stock_obj.stoploss_order_id)
                        if stock_obj.target_order_placed:
                            cancel_id, error_status = Cancel_Order(stock_obj.target_order_id)
                        Transaction.objects.filter(order_id=stock_obj.order_id, is_active=True).delete()

                        # Unsubscribe Token
                        sws.unsubscribe(correlation_id, socket_mode, [{"action": 0, "exchangeType": 1, "tokens": [stock_obj.symbol.token]}])
                        print(f"Pratik: Cancelled: Unsubscribed : {stock_obj.symbol.symbol} : {stock_obj.symbol.token}")
                        stock_obj.delete()
                        return True
                    TrailingStopLossExit(data, ltp, open_position, correlation_id, socket_mode, sws)
            except Exception as e:
                print(f'Pratik: LTP ACTION: Loop Error: {stock_obj.symbol} : {stock_obj.mode} : {e}')
        else:
            del open_position[token]
            # Unsubscribe Token
            sws.unsubscribe(correlation_id, socket_mode, [{"action": 0, "exchangeType": 1, "tokens": [token]}])
            print(f"Pratik: Token Removed: Unsubscribed : {token}")

    except Exception as e:
        print(f'Pratik: LTP ACTION: ERROR: {e}')
    return True


def connect_to_socket(correlation_id, socket_mode, subscribe_list):
    try: 
        global sws, open_position

        def on_data(wsapp, message):
            ltp = message['last_traded_price']/100
            token = message['token']
            print(f'LTP: {token} : {ltp}')
            if open_position.get(token) is False:
                open_position[token] = True
                LTP_Action(token, ltp, open_position, correlation_id, socket_mode, sws)
                if open_position.get(token):
                    open_position[token] = False

        def on_open(wsapp):
            print(f'Pratik: CONNECT TO SOCKET: Opened : {subscribe_list}')
            sws.subscribe(correlation_id, socket_mode, subscribe_list)

        def on_error(wsapp, error):
            print(f'Pratik: CONNECT TO SOCKET: Error : {error}')

        # Assign the callbacks.
        sws.on_open = on_open
        sws.on_data = on_data
        sws.on_error = on_error

        sws.connect()
    except Exception as e:
        print(f'Pratik: CONNECT TO SOCKET: ERROR: MAIN: {e}')
