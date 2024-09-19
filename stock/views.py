import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from trade.settings import sws, open_position


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
        print(f'Pratik: Api Socket Stream : Started')
        data = json.loads(request.body)

        correlation_id = data['correlation_id']
        socket_mode = int(data['socket_mode'])
        subscribe_list = data['subscribe_list']

        print(f'Pratik: Api Socket Stream : Data : {correlation_id} : {socket_mode} : {subscribe_list}')

        global sws, open_position
        for i in subscribe_list:
            for j in i['tokens']:
                open_position[j] = False
        sws.subscribe(correlation_id, socket_mode, subscribe_list)

        print(f'Pratik: Api Socket Stream: Ended')
        return HttpResponse(True)
    except Exception as e:
        print(f'Pratik: Api Socket Stream: Error : {e}')
        return HttpResponse(str(e))
