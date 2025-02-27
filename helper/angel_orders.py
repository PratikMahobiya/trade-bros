from time import sleep
from datetime import datetime
from zoneinfo import ZoneInfo
from logs.logger import create_logger, write_error_log
from option.models import OptionSymbol
from system_conf.models import Configuration
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
                angel_conn, broker_obj = AngelOne('Angel-Himanshu')
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
                angel_conn, broker_obj = AngelOne('Angel-Himanshu')
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


def ExitAction(sender, instance, created):
    try:
        system_conf_obj = Configuration.objects.filter(is_active=True)[0]
        if system_conf_obj.place_order and instance.indicate == 'EXIT':
            global angel_pratik_conn
            angel_conn = angel_pratik_conn
            book = angel_conn.orderBook()['data']
            if book is None:
                return True
            else:
                if any(ord['orderid'] == instance.order_id and ord['status'] not in ['complete'] for ord in book):
                    Place_Force_Exit(instance.symbol, instance.mode, instance.price, instance.lot, angel_conn)
    except Exception as e:
        # create or get log in db
        logger = create_logger(
            file_name=f'Global-Error_{datetime.now(tz=ZoneInfo("Asia/Kolkata")).date()}')
        write_error_log(logger, f'{e}')


def Place_Force_Exit(symbol, mode, price, lot, angel_conn):
  if symbol[:3] == 'BSE':
    exchange_seg = 'BFO'
  else:
    exchange_seg = 'NFO'
  option_symbol_obj = OptionSymbol.objects.get(symbol=symbol[:-2])
  orderparams = {
              "variety": "NORMAL",
              "tradingsymbol": option_symbol_obj.call_angel_symbol if mode == 'CE' else option_symbol_obj.put_angel_symbol,
              "symboltoken": option_symbol_obj.call_token if mode == 'CE' else option_symbol_obj.put_token,
              "transactiontype": "SELL",
              "exchange": exchange_seg,
              "ordertype": "LIMIT",
              "producttype": "CARRYFORWARD",
              "duration": "DAY",
              "price": price,
              "quantity": lot * option_symbol_obj.lot
              }
  if angel_conn:
    order_status = 'CONNECTION OK'
    order_id = angel_conn.placeOrder(orderparams)
    order_status = 'Exit-ed'
  return order_id, order_status