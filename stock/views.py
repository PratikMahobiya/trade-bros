from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from trade.settings import sws


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
        data = request.get_json()
        correlation_id = data['correlation_id']
        socket_mode = int(data['socket_mode'])
        subscribe_list = data['subscribe_list']
        print(f'Pratik: Api Socket Stream : Started : {subscribe_list}')
        global sws
        sws.subscribe(correlation_id, socket_mode, subscribe_list)
        print(f'Pratik: Api Socket Stream: Ended')
        return HttpResponse(True)
    except Exception as e:
        print(f'Pratik: Api Socket Stream: Error : {e}')
        return HttpResponse(str(e))
