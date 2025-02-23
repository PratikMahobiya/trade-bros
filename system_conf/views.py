import json
import threading
from zoneinfo import ZoneInfo
from datetime import datetime
from django.http import HttpResponse
from account.action import AccountExitAction
from trade_bros.settings import sws, open_position
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@csrf_exempt
def AwakeAPI(request):
    try:
        return HttpResponse(True)
    except Exception as e:
        return HttpResponse(str(e))


# Create your views here.
@csrf_exempt
def AccountExitApi(request):
    now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    try:
        print(f"TradeBros: Account Exit Api : Started {now.strftime('%d-%b-%Y %H:%M:%S')}")
        data = json.loads(request.body)
        print(f"TradeBros: Account Exit Api : Data {data}")

        # Streaming threads for Open Positions
        exit_thread = threading.Thread(name=f"API-Exit-{now.strftime('%d-%b-%Y %H:%M:%S')}", target=AccountExitAction, args=(data,), daemon=True)
        exit_thread.start()

        print(f'TradeBros: Account Exit Api : Execution Time(hh:mm:ss) : {(datetime.now(tz=ZoneInfo("Asia/Kolkata")) - now)}')
        return HttpResponse(True)
    except Exception as e:
        return HttpResponse(str(e))


@csrf_exempt
def SocketStream(request):
    try:
        print(f'TradeBros: Api Socket Stream : Started')
        data = json.loads(request.body)

        correlation_id = data['correlation_id']
        socket_mode = int(data['socket_mode'])
        subscribe_list = data['subscribe_list']
        product = data['product']

        print(f'TradeBros: Api Socket Stream : Data : {correlation_id} : {socket_mode} : {subscribe_list}')

        global sws, open_position
        for i in subscribe_list:
            for j in i['tokens']:
                open_position[j] = False
        
        if product == 'future':
            sws.subscribe(correlation_id, socket_mode, subscribe_list)

        print(f'TradeBros: Api Socket Stream: Ended')
        return HttpResponse(True)
    except Exception as e:
        print(f'TradeBros: Api Socket Stream: Error : {e}')
        return HttpResponse(str(e))