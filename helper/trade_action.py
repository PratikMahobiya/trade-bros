
import requests
from helper.angel_order import Create_Order
from stock.models import StockConfig, Transaction
from trade.settings import SOCKET_STREAM_URL_DOMAIN

def Price_Action_Trade(data, new_entry):
    stock_config_obj, created = StockConfig.objects.get_or_create(mode=data['mode'], symbol=data['symbol_obj'], is_active=False)
    if created:
        stock_config_obj.lot = data['lot']

        # Place Order.
        if data['product'] == 'future':
            order_id, order_status, price = Create_Order(data['configuration_obj'], 'buy', 'CARRYFORWARD', data['symbol_obj'].token, data['symbol_obj'].symbol, data['symbol_obj'].exchange, data['ltp'], data['lot'], "LIMIT")
        else:
            if data['mode'] == 'CE':
                order_id, order_status, price = Create_Order(data['configuration_obj'], 'buy', 'DELIVERY', data['symbol_obj'].token, data['symbol_obj'].symbol, data['symbol_obj'].exchange, data['ltp'], data['lot'], "LIMIT")
            else:
                order_id, order_status, price = Create_Order(data['configuration_obj'], 'sell', 'INTRADAY', data['symbol_obj'].token, data['symbol_obj'].symbol, data['symbol_obj'].exchange, data['ltp'], data['lot'], "LIMIT")
        
        stock_config_obj.lot = data['lot']
        stock_config_obj.price = price
        stock_config_obj.highest_price = price
        stock_config_obj.stoploss = round(price - price * (data['stoploss'])/100, len(str(price).split('.')[-1]))
        stock_config_obj.target = round(price + price * (data['target'])/100, len(str(price).split('.')[-1]))
        stock_config_obj.fixed_target = round(price + price * (data['fixed_target'])/100, len(str(price).split('.')[-1]))
        stock_config_obj.order_id = order_id
        stock_config_obj.order_status = order_status
        stock_config_obj.is_active = True
        stock_config_obj.trailing_sl = 0

        # Check for Resistance and Support
        # if data['mode'] == 'CE':
        #     if price < data['S3'] and stock_config_obj.fixed_target > data['S3']:
        #         stock_config_obj.fixed_target = data['S3']

        #     if price > data['S3'] and price < data['S2'] and stock_config_obj.fixed_target > data['S2']:
        #         stock_config_obj.fixed_target = data['S2']

        #     elif price > data['S2'] and price < data['S1'] and stock_config_obj.fixed_target > data['S1']:
        #         stock_config_obj.fixed_target = data['S1']

        #     elif price > data['S1'] and price < data['pivot'] and stock_config_obj.fixed_target > data['pivot']:
        #         stock_config_obj.fixed_target = data['pivot']

        #     elif price > data['pivot'] and price < data['R1'] and stock_config_obj.fixed_target > data['R1']:
        #         stock_config_obj.fixed_target = data['R1']

        #     elif price > data['R1'] and price < data['R2'] and stock_config_obj.fixed_target > data['R2']:
        #         stock_config_obj.fixed_target = data['R2']

        #     elif price > data['R2'] and price < data['R3'] and stock_config_obj.fixed_target > data['R3']:
        #         stock_config_obj.fixed_target = data['R3']
            
        #     elif price > data['R3']:
        #         pass
        
        # elif data['mode'] == 'PE':
        #     if price > data['R3'] and stock_config_obj.fixed_target < data['R3']:
        #         stock_config_obj.fixed_target = data['R3']

        #     if price < data['R3'] and price > data['R2'] and stock_config_obj.fixed_target < data['R2']:
        #         stock_config_obj.fixed_target = data['R2']

        #     elif price < data['R2'] and price > data['R1'] and stock_config_obj.fixed_target < data['R1']:
        #         stock_config_obj.fixed_target = data['R1']

        #     elif price < data['R1'] and price > data['pivot'] and stock_config_obj.fixed_target < data['pivot']:
        #         stock_config_obj.fixed_target = data['pivot']

        #     elif price < data['pivot'] and price > data['S1'] and stock_config_obj.fixed_target < data['S1']:
        #         stock_config_obj.fixed_target = data['S1']

        #     elif price < data['S1'] and price > data['S2'] and stock_config_obj.fixed_target < data['S2']:
        #         stock_config_obj.fixed_target = data['S2']

        #     elif price < data['S2'] and price > data['S3'] and stock_config_obj.fixed_target < data['S3']:
        #         stock_config_obj.fixed_target = data['S3']
            
        #     elif price < data['S3']:
        #         pass

        stock_config_obj.save()
        # TRANSACTION TABLE UPDATE
        Transaction.objects.create(
                                    product=data['symbol_obj'].product,
                                    symbol=data['symbol_obj'].symbol,
                                    mode=data['mode'],
                                    indicate='ENTRY',
                                    type='LONG' if data['mode'] == 'CE' else 'SHORT',
                                    price=price,
                                    target=stock_config_obj.target,
                                    fixed_target=stock_config_obj.fixed_target,
                                    stoploss=stock_config_obj.stoploss,
                                    order_id=stock_config_obj.order_id,
                                    order_status=stock_config_obj.order_status,
                                    lot=stock_config_obj.lot)
        print(f'Pratik: {data["log_identifier"]}: Entry on {data["product"]} : {data["symbol_obj"].name} on {price}')
        new_entry.append((data["symbol_obj"].exchange, data["symbol_obj"].name, data["symbol_obj"].token))

        # Start Socket Streaming
        correlation_id = "pratik-socket"
        socket_mode = 1
        nse = []
        nfo = []
        bse = []
        bfo = []
        mcx = []

        if data["symbol_obj"].exchange == 'NSE':
            nse.append(data["symbol_obj"].token)
        elif data["symbol_obj"].exchange == 'NFO':
            nfo.append(data["symbol_obj"].token)
        elif data["symbol_obj"].exchange == 'BSE':
            bse.append(data["symbol_obj"].token)
        elif data["symbol_obj"].exchange == 'BFO':
            bfo.append(data["symbol_obj"].token)
        else:
            mcx.append(data["symbol_obj"].token)

        subscribe_list = []
        for index, i in enumerate((nse,nfo,bse,bfo,mcx)):
            if i:
                subscribe_list.append({
                    "exchangeType": index+1,
                    "tokens": i
                })
        url = f"{SOCKET_STREAM_URL_DOMAIN}/api/trade/socket-stream/"
        data = {
            "subscribe_list": subscribe_list,
            "correlation_id": correlation_id,
            "socket_mode": socket_mode
        }
        response = requests.post(url, json=data, verify=False)
        print(f'Pratik: {data["log_identifier"]}: New Entries: Streaming Response: {response.status_code}')
    return new_entry
