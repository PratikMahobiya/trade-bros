from option.models import Transaction
from helper.angel_orders import Cancel_Order, Exit_Order, Order_Status
from logs.logger import write_info_log


def TrailingTargetUpdate(data, ltp):
    # TARGET Exit
    if (ltp >= data['stock_obj'].target):
        data['stock_obj'].tr_hit = True
        data['stock_obj'].target =  round(ltp + ltp * data['target'], 2)
        data['stock_obj'].trailing_sl = round(ltp - ltp * data['stoploss'], 2)
        data['stock_obj'].save()
        return True
    return False


def TargetExit(data, ltp):
    # TARGET Exit
    if (ltp > data['stock_obj'].fixed_target): #(ltp >= data['stock_obj'].target) or 
        if data['configuration'].place_order and not Order_Status(data['stock_obj'].order_id, data['conn']):
            order_id, order_status = Cancel_Order(data['stock_obj'].order_id, data['conn'])
            data['stock_obj'].delete()
            Transaction.objects.filter(order_id=data['stock_obj'].order_id).delete()
            return True

        order_id, order_status = Exit_Order(data['configuration'], data['stock_obj'], ltp, data['conn'])

        if data['configuration'].place_order and (order_id in ['', 0, '0', None]):
            write_info_log(data['logger'], f'ANGEL EXIT: NOT ACCEPTING ORDER {order_id}, {order_status}')
            return True

        diff = (ltp - data['stock_obj'].price)
        profit = round((((diff/data['stock_obj'].price) * 100)), 2)
        # TRANSACTION TABLE UPDATE
        symbol_ = f"{data['stock_obj'].symbol}{data['stock_obj'].mode}"
        Transaction.objects.create(mode=data['stock_obj'].mode,
                                    index=data['stock_obj'].symbol.index,
                                    symbol=symbol_,
                                    indicate='EXIT',
                                    type='TARGET',
                                    price=ltp,
                                    stoploss=data['stock_obj'].stoploss,
                                    target=data['stock_obj'].target,
                                    fixed_target=data['stock_obj'].fixed_target,
                                    profit=profit,
                                    max=data['stock_obj'].max,
                                    max_l=data['stock_obj'].max_l,
                                    highest_price=data['stock_obj'].highest_price,
                                    order_id=order_id,
                                    order_status=order_status,
                                    lot=data['stock_obj'].lot)
        write_info_log(data['logger'], f'Exit of {symbol_} on price {ltp} : SQROFF : {order_id}')
        data['stock_obj'].delete()
    return True


def TrailingStopLossExit(data, ltp):
    # StopLoss and Trailing StopLoss Exit
    price_value, exit_type = (data['stock_obj'].trailing_sl, 'TR-SL') if data['stock_obj'].tr_hit else (data['stock_obj'].stoploss, 'STOPLOSS')
    if (ltp <= price_value):
        if data['configuration'].place_order and not Order_Status(data['stock_obj'].order_id, data['conn']):
            order_id, order_status = Cancel_Order(data['stock_obj'].order_id, data['conn'])
            data['stock_obj'].delete()
            Transaction.objects.filter(order_id=data['stock_obj'].order_id).delete()
            return True

        if exit_type == 'STOPLOSS':
            data['configuration'].sell_market_order = True

        order_id, order_status = Exit_Order(data['configuration'], data['stock_obj'], ltp, data['conn'])

        if data['configuration'].place_order and (order_id in ['', 0, '0', None]):
            write_info_log(data['logger'], f'ANGEL EXIT: NOT ACCEPTING ORDER {order_id}, {order_status}')
            return True

        diff = (ltp - data['stock_obj'].price)
        profit = round((((diff/data['stock_obj'].price) * 100)), 2)
        # TRANSACTION TABLE UPDATE
        symbol_ = f"{data['stock_obj'].symbol}{data['stock_obj'].mode}"
        Transaction.objects.create(mode=data['stock_obj'].mode,
                                    index=data['stock_obj'].symbol.index,
                                    symbol=symbol_,
                                    indicate='EXIT',
                                    type=exit_type,
                                    price=ltp,
                                    stoploss=data['stock_obj'].stoploss,
                                    target=data['stock_obj'].target,
                                    fixed_target=data['stock_obj'].fixed_target,
                                    profit=profit,
                                    max=data['stock_obj'].max,
                                    max_l=data['stock_obj'].max_l,
                                    highest_price=data['stock_obj'].highest_price,
                                    order_id=order_id,
                                    order_status=order_status,
                                    lot=data['stock_obj'].lot)
        write_info_log(data['logger'], f'Exit of {symbol_} on price {ltp} : SQROFF : {order_id}')
        data['stock_obj'].delete()
    return True


def SquareOff(data, ltp):
    # Place Order.
    exit_type = 'SQROFF'
    if data['configuration'].place_order and not Order_Status(data['stock_obj'].order_id, data['conn']):
        order_id, order_status = Cancel_Order(data['stock_obj'].order_id, data['conn'])
        data['stock_obj'].delete()
        Transaction.objects.filter(order_id=data['stock_obj'].order_id).delete()
        return True

    order_id, order_status = Exit_Order(data['configuration'], data['stock_obj'], ltp, data['conn'])

    if data['configuration'].place_order and (order_id in ['', 0, '0', None]):
        write_info_log(data['logger'], f'ANGEL EXIT: NOT ACCEPTING ORDER {order_id}, {order_status}')
        return True

    diff = (ltp - data['stock_obj'].price)
    profit = round((((diff/data['stock_obj'].price) * 100)), 2)
    # TRANSACTION TABLE UPDATE
    symbol_ = f"{data['stock_obj'].symbol}{data['stock_obj'].mode}"
    Transaction.objects.create(mode=data['stock_obj'].mode,
                                index=data['stock_obj'].symbol.index,
                                symbol=symbol_,
                                indicate='EXIT',
                                type=exit_type,
                                price=ltp,
                                stoploss=data['stock_obj'].stoploss,
                                target=data['stock_obj'].target,
                                fixed_target=data['stock_obj'].fixed_target,
                                profit=profit,
                                max=data['stock_obj'].max,
                                max_l=data['stock_obj'].max_l,
                                highest_price=data['stock_obj'].highest_price,
                                order_id=order_id,
                                order_status=order_status,
                                lot=data['stock_obj'].lot)
    write_info_log(data['logger'], f'Exit of {symbol_} on price {ltp} : SQROFF : {order_id}')
    data['stock_obj'].delete()
    return True