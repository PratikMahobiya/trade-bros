from task import socket_setup
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


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
        socket_setup()
        print(f'Pratik: Api Socket Stream: Started')
        return HttpResponse(True)
    except Exception as e:
        print(f'Pratik: Api Socket Stream: Error : {e}')
        return HttpResponse(str(e))