from stock.models import Transaction
from helper.angel_order import Create_Order


def TrailingTargetUpdate(data, ltp):
    # TARGET Exit
    if (ltp >= data['stock_obj'].target):
        data['stock_obj'].tr_hit = True
        data['stock_obj'].target =  round(ltp + ltp * data['target'], len(str(ltp).split('.')[-1]))
        data['stock_obj'].trailing_sl = round(ltp - ltp * data['stoploss'], len(str(ltp).split('.')[-1]))
        data['stock_obj'].save()
        return True
    return False


def TargetExit(data, ltp, open_position, correlation_id, socket_mode, sws):
    # TARGET Exit
    if (ltp > data['stock_obj'].fixed_target):
        # Exit Order.
        if data['stock_obj'].symbol.product == 'future':
            order_id, order_status, price = Create_Order(data['configuration_obj'], 'sell', 'CARRYFORWARD', data['stock_obj'].symbol.token, data['stock_obj'].symbol.symbol, data['stock_obj'].symbol.exchange, ltp, data['stock_obj'].lot, "MARKET")
        else:
            if data['stock_obj'].mode == 'CE':
                order_id, order_status, price = Create_Order(data['configuration_obj'], 'sell', 'DELIVERY', data['stock_obj'].symbol.token, data['stock_obj'].symbol.symbol, data['stock_obj'].symbol.exchange, ltp, data['stock_obj'].lot, "MARKET")
            else:
                order_id, order_status, price = Create_Order(data['configuration_obj'], 'buy', 'INTRADAY', data['stock_obj'].symbol.token, data['stock_obj'].symbol.symbol, data['stock_obj'].symbol.exchange, ltp, data['stock_obj'].lot, "MARKET")

        if data['configuration_obj'].place_order and (order_id in ['', 0, '0', None]):
            print(f"Pratik: TARGET EXIT: ERROR: Not Accepting Orders: {data['stock_obj'].symbol} : {order_id}, {order_status}")
            return False

        del open_position[data['stock_obj'].symbol.token]
        diff = (price - data['stock_obj'].price)
        profit = round((((diff/data['stock_obj'].price) * 100)), 2)
        # TRANSACTION TABLE UPDATE
        Transaction.objects.create(
                                product=data['stock_obj'].symbol.product,
                                mode=data['stock_obj'].mode,
                                symbol=data['stock_obj'].symbol.symbol,
                                indicate='EXIT',
                                type='TARGET',
                                price=price,
                                target=data['stock_obj'].target,
                                stoploss=data['stock_obj'].stoploss,
                                profit=profit,
                                max=data['stock_obj'].max,
                                max_l=data['stock_obj'].max_l,
                                highest_price=data['stock_obj'].highest_price,
                                order_id=order_id,
                                order_status=order_status,
                                fixed_target=data['stock_obj'].fixed_target,
                                lot=data['stock_obj'].lot)
        sws.unsubscribe(correlation_id, socket_mode, [{"action": 0, "exchangeType": 1, "tokens": [data['stock_obj'].symbol.token]}])
        print(f"Pratik: TARGET EXIT: Unsubscribed : {data['stock_obj'].symbol.symbol} : {data['stock_obj'].symbol.token}")
        data['stock_obj'].delete()
    return True


def TrailingStopLossExit(data, ltp, open_position, correlation_id, socket_mode, sws):
    # StopLoss and Trailing StopLoss Exit
    price_value, exit_type = (data['stock_obj'].trailing_sl, 'TR-SL') if data['stock_obj'].tr_hit else (data['stock_obj'].stoploss, 'STOPLOSS')
    if (ltp <= price_value):
        # Exit Order.
        if data['stock_obj'].symbol.product == 'future':
            order_id, order_status, price = Create_Order(data['configuration_obj'], 'sell', 'CARRYFORWARD', data['stock_obj'].symbol.token, data['stock_obj'].symbol.symbol, data['stock_obj'].symbol.exchange, ltp, data['stock_obj'].lot, "MARKET")
        else:
            if data['stock_obj'].mode == 'CE':
                order_id, order_status, price = Create_Order(data['configuration_obj'], 'sell', 'DELIVERY', data['stock_obj'].symbol.token, data['stock_obj'].symbol.symbol, data['stock_obj'].symbol.exchange, ltp, data['stock_obj'].lot, "MARKET")
            else:
                order_id, order_status, price = Create_Order(data['configuration_obj'], 'buy', 'INTRADAY', data['stock_obj'].symbol.token, data['stock_obj'].symbol.symbol, data['stock_obj'].symbol.exchange, ltp, data['stock_obj'].lot, "MARKET")

        if data['configuration_obj'].place_order and (order_id in ['', 0, '0', None]):
            print(f"Pratik: TRAILING/STOPLOSS EXIT: ERROR: Not Accepting Orders: {data['stock_obj'].symbol} : {order_id}, {order_status}")
            return False

        del open_position[data['stock_obj'].symbol.token]
        # diff = (price - data['stock_obj'].price)
        diff = (price_value - data['stock_obj'].price)
        profit = round((((diff/data['stock_obj'].price) * 100)), 2)
        # TRANSACTION TABLE UPDATE
        Transaction.objects.create(
                                product=data['stock_obj'].symbol.product,
                                mode=data['stock_obj'].mode,
                                symbol=data['stock_obj'].symbol.symbol,
                                indicate='EXIT',
                                type=exit_type,
                                # price=price,
                                price=price_value,
                                target=data['stock_obj'].target,
                                stoploss=data['stock_obj'].stoploss,
                                profit=profit,
                                max=data['stock_obj'].max,
                                max_l=data['stock_obj'].max_l,
                                highest_price=data['stock_obj'].highest_price,
                                order_id=order_id,
                                order_status=order_status,
                                fixed_target=data['stock_obj'].fixed_target,
                                lot=data['stock_obj'].lot)
        sws.unsubscribe(correlation_id, socket_mode, [{"action": 0, "exchangeType": 1, "tokens": [data['stock_obj'].symbol.token]}])
        print(f"Pratik: TRAILING/STOPLOSS EXIT: Unsubscribed : {data['stock_obj'].symbol.symbol} : {data['stock_obj'].symbol.token}")
        data['stock_obj'].delete()
    return False
