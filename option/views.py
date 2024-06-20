from datetime import datetime
from zoneinfo import ZoneInfo
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from logs.logger import create_logger, write_info_log

# Create your views here.
@csrf_exempt
def AwakeAPI(request):
    try:
        # create or get log in db
        logger = create_logger(
            file_name=f'awake-{datetime.now(tz=ZoneInfo("Asia/Kolkata")).date()}')
        write_info_log(logger, f'API Time: {datetime.now(tz=ZoneInfo("Asia/Kolkata")).strftime("%d-%b-%Y %H:%M:%S")}')
        return HttpResponse(True)
    except Exception as e:
        return HttpResponse(str(e))