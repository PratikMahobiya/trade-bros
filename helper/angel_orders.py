from time import sleep
from helper.connection import AngelOne


def Order_Status(order_id, angel_conn):
    book = angel_conn.orderBook()['data']
    if book is None:
      return True
    return any(
        ord['orderid'] == order_id and ord['status'] in ['complete']
        for ord in book
    )


def Create_Order(system_conf_obj, stock_config_obj, price, angel_conn=None):
    # Place an order
    order_id = 0
    order_status = 'Not Placed' if system_conf_obj.place_order else 'In-Active'
    try:
        symbol = stock_config_obj.symbol.call_angel_symbol if stock_config_obj.mode == 'CE' else stock_config_obj.symbol.put_angel_symbol
        token = stock_config_obj.symbol.call_token if stock_config_obj.mode == 'CE' else stock_config_obj.symbol.put_token
        quantity = stock_config_obj.lot * stock_config_obj.symbol.lot
        if stock_config_obj.symbol.symbol[:3] == 'BSE':
            exchange_seg = 'BFO'
        else:
            exchange_seg = 'NFO'
        orderparams = {
                    "variety": "NORMAL",
                    "tradingsymbol": symbol,
                    "symboltoken": token,
                    "transactiontype": "BUY",
                    "exchange": exchange_seg,
                    # "ordertype": "MARKET",
                    "producttype": "CARRYFORWARD",
                    "duration": "DAY",
                    # "price": price,
                    "quantity": quantity
                    }

        if system_conf_obj.buy_market_order:
            orderparams['ordertype'] = "MARKET"
        else:
            orderparams['ordertype'] = "LIMIT"
            orderparams['price'] = price

        if system_conf_obj.place_order:
            if not angel_conn:
                # sleep(1)
                angel_conn, broker_obj = AngelOne('Angel-Pratik')
            if angel_conn:
                order_status = 'CONNECTION OK'
                order_id = angel_conn.placeOrder(orderparams)
                order_status = 'Placed'
    except Exception as e:
        order_status = f"{e} : {price} : {order_status} : {orderparams}"
    return order_id, order_status, price


def Exit_Order(system_conf_obj, stock_config_obj, price, angel_conn=None):
    # Place an order
    order_id = 0
    order_status = 'Not Placed' if system_conf_obj.place_order else 'In-Active'
    try:
        if stock_config_obj.symbol.symbol[:3] == 'BSE':
            exchange_seg = 'BFO'
        else:
            exchange_seg = 'NFO'
        orderparams = {
                    "variety": "NORMAL",
                    "tradingsymbol": stock_config_obj.symbol.call_angel_symbol if stock_config_obj.mode == 'CE' else stock_config_obj.symbol.put_angel_symbol,
                    "symboltoken": stock_config_obj.symbol.call_token if stock_config_obj.mode == 'CE' else stock_config_obj.symbol.put_token,
                    "transactiontype": "SELL",
                    "exchange": exchange_seg,
                    # "ordertype": "MARKET" if system_conf_obj.sell_market_order else "LIMIT",
                    "producttype": "CARRYFORWARD",
                    "duration": "DAY",
                    # "price": price,
                    "quantity": stock_config_obj.lot * stock_config_obj.symbol.lot
                    }
        
        if system_conf_obj.sell_market_order:
            orderparams['ordertype'] = "MARKET"
        else:
            orderparams['ordertype'] = "LIMIT"
            orderparams['price'] = price

        if system_conf_obj.place_order:
            if not angel_conn:
                # sleep(1)
                angel_conn, broker_obj = AngelOne('Angel-Pratik')
            if angel_conn:
                order_status = 'CONNECTION OK'
                order_id = angel_conn.placeOrder(orderparams)
                order_status = 'Exit-ed'
    except Exception as e:
        order_status = f"{e} : {price} : {order_status} : {orderparams}"
    return order_id, order_status


def Cancel_Order(order_id, angel_conn):
 # Place an order for exit
  cancel_id = 0
  error_status = 'Not Cancelled'
  try:
    cancel_id = angel_conn.cancelOrder(order_id=order_id,
                                  variety="NORMAL")['data']['orderid']
    error_status = 'Cancelled'
  except Exception as e:
    error_status = e.args[0]
  return cancel_id, error_status