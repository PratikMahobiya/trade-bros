from time import sleep
from django.http import HttpResponse
from stock.models import StockConfig
from django.views.decorators.csrf import csrf_exempt
from trade.settings import BROKER_API_KEY, BROKER_USER_ID, broker_connection, sws


# Create your views here.
@csrf_exempt
def AwakeAPI(request):
    try:
        return HttpResponse(True)
    except Exception as e:
        return HttpResponse(str(e))


@csrf_exempt
def SocketStream(request):
    try:
        print(f'Pratik: Api Socket Stream: Started')
        global broker_connection, sws
        open_position = {}
    
        BROKER_AUTH_TOKEN = broker_connection.access_token
        BROKER_FEED_TOKEN = broker_connection.feed_token

        try:
            sws.close_connection()
            print(f'Pratik: Api Socket Stream: Connection Closed')
            sleep(2)
        except Exception as e:
            print(f'Pratik: Api Socket Streamp: Trying to close the connection : {e}')
    
        correlation_id = "pratik-socket"
        mode = 1
        nse = []
        nfo = []
        bse = []
        bfo = []
        mcx = []
    
        for i in StockConfig.objects.filter(is_active=True):
            open_position[i.symbol.token] = False
            if i.symbol.exchange == 'NSE':
                nse.append(i.symbol.token)
            elif i.symbol.exchange == 'NFO':
                nfo.append(i.symbol.token)
            elif i.symbol.exchange == 'BSE':
                bse.append(i.symbol.token)
            elif i.symbol.exchange == 'BFO':
                bfo.append(i.symbol.token)
            else:
                mcx.append(i.symbol.token)
    
        subscribe_list = []
        for index, i in enumerate((nse,nfo,bse,bfo,mcx)):
            if i:
                subscribe_list.append({
                    "exchangeType": index+1,
                    "tokens": i
                })
        
        # Streaming threads for Open Positions
        if subscribe_list:
            sws = SmartWebSocketV2(BROKER_AUTH_TOKEN, BROKER_API_KEY, BROKER_USER_ID, BROKER_FEED_TOKEN)
            socket_thread = threading.Thread(name=f"Streaming-{now.strftime('%d-%b-%Y %H:%M:%S')}", target=connect_to_socket, args=(correlation_id, mode, subscribe_list, open_position), daemon=True)
            socket_thread.start()
        print(f'Pratik: Api Socket Stream: Ended')
        return HttpResponse(True)
    except Exception as e:
        print(f'Pratik: Api Socket Stream: Error : {e}')
        return HttpResponse(str(e))
