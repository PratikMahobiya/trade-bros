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
            data = broker_connection.placeOrderFullResponse(orderparams)
            order_id = f"{data['data']['uniqueorderid']}@{data['data']['orderid']}"
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
        order_id = order_id.split('@')[-1]
        data = broker_connection.cancelOrder(order_id=order_id,
                                    variety="NORMAL")
        cancel_id = f"{data['data']['uniqueorderid']}@{data['data']['orderid']}"
        error_status = 'Cancelled'
    except Exception as e:
        error_status = str(e)
    return cancel_id, error_status


def Is_Order_Completed(order_id):
    global broker_connection
    order_id = order_id.split('@')[0]
    data = broker_connection.individual_order_details(order_id)
    if data['data'] is not None:
        order_status = data['data']['orderstatus']
        if order_status in ['complete']:
            return True
    return False