from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from task import socket_setup


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
        symbol = request.GET.getlist('symbol')
        print(f'Pratik: Api Socket Stream: Started : {symbol}')
        socket_setup(log_identifier='Api')
        print(f'Pratik: Api Socket Stream: Ended')
        return HttpResponse(True)
    except Exception as e:
        print(f'Pratik: Api Socket Stream: Error : {e}')
        return HttpResponse(str(e))
