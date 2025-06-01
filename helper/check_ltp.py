from stock.models import Transaction


def TrailingTargetUpdate(data, ltp):
    # TARGET Exit
    if (ltp >= data['stock_obj'].target):
        data['stock_obj'].tr_hit = True
        if data['stock_obj'].symbol.product == 'future':
            data['stock_obj'].target =  round(ltp + ltp * data['target'], len(str(ltp).split('.')[-1]))
            data['stock_obj'].trailing_sl = round(ltp - ltp * data['stoploss'], len(str(ltp).split('.')[-1]))
        data['stock_obj'].save()
        return True
    return False


def TargetExit(data, ltp, open_position, correlation_id, socket_mode, sws):
    # TARGET Exit
    # Exit Order.

    price = ltp
    del open_position[data['stock_obj'].symbol.token]
    diff = (price - data['stock_obj'].price)
    profit = round((((diff/data['stock_obj'].price) * 100)), 2)
    # TRANSACTION TABLE UPDATE

    type = 'TARGET'
    lot = data['stock_obj'].lot
    if data['stock_obj'].symbol.product == 'future':
        price = data['stock_obj'].ltp
        diff = (price - data['stock_obj'].price)
        profit = round((((diff/data['stock_obj'].price) * 100)), 2)
        type = 'TARGET' if ((not data['socket_data'] and data['stock_obj'].mode == 'CE' and ltp >= data['stock_obj'].fixed_target) or (not data['socket_data'] and data['stock_obj'].mode == 'PE' and ltp <= data['stock_obj'].fixed_target)) else 'CS-TARGET'
        lot = data['stock_obj'].lot if ((not data['socket_data'] and data['stock_obj'].mode == 'CE' and ltp >= data['stock_obj'].fixed_target) or (not data['socket_data'] and data['stock_obj'].mode == 'PE' and ltp <= data['stock_obj'].fixed_target)) else data['stock_obj'].lot/2

    transaction_obj, _ = Transaction.objects.get_or_create(
                            product=data['stock_obj'].symbol.product,
                            mode=data['stock_obj'].mode,
                            symbol=data['stock_obj'].symbol.symbol,
                            name=data['stock_obj'].symbol.name,
                            token=data['stock_obj'].symbol.token,
                            exchange=data['stock_obj'].symbol.exchange,
                            indicate='EXIT',
                            type=type,
                            price=price,
                            target=data['stock_obj'].target,
                            stoploss=data['stock_obj'].stoploss,
                            profit=profit,
                            max=data['stock_obj'].max,
                            max_l=data['stock_obj'].max_l,
                            highest_price=data['stock_obj'].highest_price,
                            fixed_target=data['stock_obj'].fixed_target,
                            lot=lot,
                            chart_price=data['stock_obj'].chart_price)
    if data['stock_obj'].symbol.product == 'future':
        if (not data['socket_data'] and data['stock_obj'].mode == 'CE' and ltp >= data['stock_obj'].fixed_target) or (not data['socket_data'] and data['stock_obj'].mode == 'PE' and ltp <= data['stock_obj'].fixed_target): 
            data['stock_obj'].delete()
            if data['stock_obj'].symbol.exchange == 'NSE':
                exchangeType = 1
            elif data['stock_obj'].symbol.exchange == 'NFO':
                exchangeType = 2
            elif data['stock_obj'].symbol.exchange == 'BSE':
                exchangeType = 3
            elif data['stock_obj'].symbol.exchange == 'BFO':
                exchangeType = 4
            else:
                exchangeType = 5
            sws.unsubscribe(correlation_id, socket_mode, [{"action": 0, "exchangeType": exchangeType, "tokens": [data['stock_obj'].symbol.token]}])
            print(f"TradeBros: TARGET EXIT: Unsubscribed : {data['stock_obj'].symbol.symbol} : {data['stock_obj'].symbol.token}")
        else:
            open_position[data['stock_obj'].symbol.token] = False
            data['stock_obj'].capital_save = True
            data['stock_obj'].lot = lot
            data['stock_obj'].save()
    else:
        data['stock_obj'].delete()
    return True


def TrailingStopLossExit(data, ltp, open_position, correlation_id, socket_mode, sws):
    # StopLoss and Trailing StopLoss Exit
    price_value, exit_type = (data['stock_obj'].trailing_sl, 'TR-SL') if data['stock_obj'].tr_hit else (data['stock_obj'].stoploss, 'STOPLOSS')
    if (data['stock_obj'].mode == 'CE' and ltp <= price_value) or (data['stock_obj'].mode == 'PE' and ltp >= price_value) or data['percent'] < -data['configuration_obj'].fixed_target/2:
        # Exit Order.

        del open_position[data['stock_obj'].symbol.token]
        # diff = (price - data['stock_obj'].price)
        diff = (ltp - data['stock_obj'].price)
        profit = round((((diff/data['stock_obj'].price) * 100)), 2)

        if data['stock_obj'].symbol.product == 'future':
            ltp = data['stock_obj'].ltp
            diff = (ltp - data['stock_obj'].price)
            profit = round((((diff/data['stock_obj'].price) * 100)), 2)
        # TRANSACTION TABLE UPDATE
        transaction_obj, _ = Transaction.objects.get_or_create(
                                product=data['stock_obj'].symbol.product,
                                mode=data['stock_obj'].mode,
                                symbol=data['stock_obj'].symbol.symbol,
                                name=data['stock_obj'].symbol.name,
                                token=data['stock_obj'].symbol.token,
                                exchange=data['stock_obj'].symbol.exchange,
                                indicate='EXIT',
                                type=exit_type,
                                price=ltp,
                                target=data['stock_obj'].target,
                                stoploss=data['stock_obj'].stoploss,
                                profit=profit,
                                max=data['stock_obj'].max,
                                max_l=data['stock_obj'].max_l,
                                highest_price=data['stock_obj'].highest_price,
                                fixed_target=data['stock_obj'].fixed_target,
                                lot=data['stock_obj'].lot,
                                chart_price=data['stock_obj'].chart_price)
        data['stock_obj'].delete()
        if data['stock_obj'].symbol.product == 'future':
            if data['stock_obj'].symbol.exchange == 'NSE':
                exchangeType = 1
            elif data['stock_obj'].symbol.exchange == 'NFO':
                exchangeType = 2
            elif data['stock_obj'].symbol.exchange == 'BSE':
                exchangeType = 3
            elif data['stock_obj'].symbol.exchange == 'BFO':
                exchangeType = 4
            else:
                exchangeType = 5
            sws.unsubscribe(correlation_id, socket_mode, [{"action": 0, "exchangeType": exchangeType, "tokens": [data['stock_obj'].symbol.token]}])
            print(f"TradeBros: TRAILING/STOPLOSS EXIT: Unsubscribed : {data['stock_obj'].symbol.symbol} : {data['stock_obj'].symbol.token}")
    return True