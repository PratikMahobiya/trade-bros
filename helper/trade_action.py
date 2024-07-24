from option.models import OptionSymbol, StockConfig, Transaction
from helper.angel_orders import Create_Order, Exit_Order, Order_Status, Cancel_Order


def Price_Action_Trade(data):
    # Regular Trades Execution
    stock_config_obj, created = StockConfig.objects.get_or_create(
                    mode=data['mode'],
                    symbol=OptionSymbol.objects.get(symbol=data['symbol'][:-2], is_active=True),
                    is_active=True)
    if created:
        lot = 1
        while True:
            price = data['price'] * (lot * stock_config_obj.symbol.lot)
            if price >= data['configuration'].amount:
                lot = lot - 1
                break
            lot += 1
        data['lot'] = lot
        stock_config_obj.lot = data['lot']

        # Place Order.
        order_id, order_status, price = Create_Order(data['configuration'], stock_config_obj, data['price'], data['angel_conn'])
        stock_config_obj.lot = lot
        stock_config_obj.price = price
        stock_config_obj.stoploss = round(price - price * (data['stoploss'])/100, 2)
        stock_config_obj.target = round(price + price * (data['target'])/100, 2)
        stock_config_obj.fixed_target = round(price + price * (data['fixed_target'])/100, 2)
        stock_config_obj.order_id = order_id
        stock_config_obj.order_status = order_status
        stock_config_obj.save()
        # TRANSACTION TABLE UPDATE
        Transaction.objects.create(mode=data['mode'],
                                    index=stock_config_obj.symbol.index,
                                    symbol=data['symbol'],
                                    indicate='ENTRY',
                                    type='BUY',
                                    price=price,
                                    target=stock_config_obj.target,
                                    fixed_target=stock_config_obj.fixed_target,
                                    stoploss=stock_config_obj.stoploss,
                                    order_id=stock_config_obj.order_id,
                                    order_status=stock_config_obj.order_status,
                                    lot=stock_config_obj.lot)
    return True


def ForceExit(stock_obj_list, fyers_conn, angel_conn, configuration_obj):
    for stock_obj in stock_obj_list:
        # Place Order.
        if configuration_obj.place_order and not Order_Status(stock_obj.order_id, angel_conn):
            order_id, order_status = Cancel_Order(stock_obj.order_id, angel_conn)
            stock_obj.delete()
            Transaction.objects.filter(order_id=stock_obj.order_id).delete()
            return True

        price = fyers_conn.quotes({"symbols": f"{stock_obj.symbol.symbol}{stock_obj.mode}"})['d'][0]['v']['lp']
        order_id, order_status = Exit_Order(configuration_obj, stock_obj, price, angel_conn)

        diff = (price - stock_obj.price)
        profit = round((((diff/stock_obj.price) * 100)), 2)
        type_exit = 'F-EXIT'
        Transaction.objects.create(mode=stock_obj.mode,
                                    index=stock_obj.symbol.index,
                                    symbol=f"{stock_obj.symbol}{stock_obj.mode}",
                                    indicate='EXIT',
                                    type=type_exit,
                                    price=price,
                                    target=stock_obj.target,
                                    stoploss=stock_obj.stoploss,
                                    fixed_target=stock_obj.fixed_target,
                                    profit=profit,
                                    max=stock_obj.max,
                                    max_l=stock_obj.max_l,
                                    highest_price=stock_obj.highest_price,
                                    order_id=order_id,
                                    order_status=order_status,
                                    lot=stock_obj.lot)
    return True
