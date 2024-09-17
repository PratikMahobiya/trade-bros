from trade.settings import broker_connection

def Create_Order(configuration_obj, transactiontype, producttype, token, symbol, exchange, price, quantity, ordertype):
    # Place an order
    order_id = 0
    order_status = 'Not Placed' if configuration_obj.place_order else 'In-Active'
    try:
        orderparams = {
                    "variety": "NORMAL",
                    "tradingsymbol": symbol,
                    "symboltoken": token,
                    "transactiontype": transactiontype,
                    "producttype": producttype,
                    "exchange": exchange,
                    "duration": "DAY",
                    "quantity": quantity
                    }

        if ordertype == "MARKET":
            orderparams['ordertype'] = "MARKET"
        else:
            orderparams['ordertype'] = "LIMIT"
            orderparams['price'] = price

        if configuration_obj.place_order:
            global broker_connection
            order_id = broker_connection.placeOrder(orderparams)
            order_status = 'Placed'
    except Exception as e:
        order_status = f"{e} : {price} : {order_status} : {orderparams}"
    return order_id, order_status, price


def Cancel_Order(order_id):
 # Place an order for exit
  cancel_id = 0
  error_status = 'Not Cancelled'
  try:
    global broker_connection
    cancel_id = broker_connection.cancelOrder(order_id=order_id,
                                  variety="NORMAL")['data']['orderid']
    error_status = 'Cancelled'
  except Exception as e:
    error_status = e.args[0]
  return cancel_id, error_status
