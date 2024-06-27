from datetime import datetime, time
from zoneinfo import ZoneInfo
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Count, Sum

from option.models import Index, StockConfig, Transaction, DailyRecord

# Create your views here.
@csrf_exempt
def DailyRecordAPI(request):
    try:
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", 5)
        query_set = DailyRecord.objects.filter(
            is_active=True
        ).order_by('-created_at')
        paginator = Paginator(query_set, per_page)
        page_obj = paginator.get_page(page)
        data = page_obj.object_list.values()

        payload = {
            "page": {
                "current": page_obj.number,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "data": list(data)
        }
    except Exception as e:
        payload = {
            'error': str(e)
        }
    return JsonResponse(payload)


# Create your views here.
@csrf_exempt
def TransactionAPI(request):
    try:
        page = request.GET.get("page", 1)
        per_page = request.GET.get("per_page", 5)
        query_set = Transaction.objects.filter(
            is_active=True
        ).order_by('-date')
        paginator = Paginator(query_set, per_page)
        page_obj = paginator.get_page(page)
        data = page_obj.object_list.values()

        payload = {
            "page": {
                "current": page_obj.number,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
            "data": list(data)
        }
    except Exception as e:
        payload = {
            'error': str(e)
        }
    return JsonResponse(payload)
    

# Create your views here.
@csrf_exempt
def StatusAPI(request):
    try:
        now = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
        transaction_list = Transaction.objects.filter(date__date = datetime.now().date(), indicate='EXIT', is_active=True).values('index').annotate(profit=Sum('profit'), trade=Count('indicate'))
        index_wise_str = ''
        index_status = {}
        for trans_obj in transaction_list:
            index_status[trans_obj['index']] = {}
            index_obj = Index.objects.get(index=trans_obj['index'])
            days_difference = (index_obj.expiry_date - now.date()).days
            if index_obj.expiry_date == now.date() or ((index_obj.expiry_date - now.date()).days == 7):
                daily_target = index_obj.fixed_target + 5
            else:
                daily_target = round(index_obj.fixed_target/(days_difference+1), 2)
            if round(trans_obj['profit'], 2) > daily_target:
                target_status = "Achived "
            else:
                target_status = "Yet to achive "
            index_wise_str = trans_obj['index'] + ": P/L of " + str(round(trans_obj['profit'], 2)) + '%' + ' : on ' + str(trans_obj['trade']) + " trades, target status: " + target_status + str(daily_target) + '%'
            if round(trans_obj['profit'], 2) > daily_target:
                index_status[trans_obj['index']]['green'] = index_wise_str
            elif now.time() > time(15, 15, 00) and round(trans_obj['profit'], 2) < daily_target:
                if round(trans_obj['profit'], 2) > 0:
                    index_wise_str = index_wise_str.replace(target_status, 'Achived ')
                    index_status[trans_obj['index']]['green'] = index_wise_str
                else:
                    index_wise_str = index_wise_str.replace(target_status, 'Failed to achive ')
                    index_status[trans_obj['index']]['red'] = index_wise_str
            else:
                index_status[trans_obj['index']]['yellow'] = index_wise_str
        
        if index_wise_str == '':
            index_status['NoTrade']['green'] = "No Trade Today"
        
        # Calculate the first day of the next month
        month_first_day = datetime(datetime.now().year, datetime.now().month, 1)
        total_entry = Transaction.objects.filter(indicate='EXIT', created_at__gte=month_first_day,  is_active=True).order_by('date').count()
        accuracy = round((len(Transaction.objects.filter(profit__gte=0, indicate='EXIT', created_at__gte=month_first_day, is_active=True))/total_entry) * 100, 2)
        return_1 = round(sum(Transaction.objects.filter(indicate='EXIT', created_at__gte=month_first_day, is_active=True).values_list('profit', flat=True)), 2)

        month_status = {}
        if return_1 > 0:
            month_status['green'] = f"This month we are in profit of {return_1} % on {total_entry} trades with accuracy of {accuracy} %."
        else:
            month_status['red'] = f"This month we are in loss of {return_1} % on {total_entry} trades with accuracy of {accuracy} %."

        today_status = {}

        today_status['entry'] = len(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='ENTRY'))
        today_status['exit'] = len(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT'))
        today_status['active'] = len(StockConfig.objects.filter(is_active=True))
        today_status['p_l'] = round(sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT').values_list('profit', flat=True)), 2)

        payload = {
            'month' : month_status,
            'index' : index_status,
            'today' : today_status
        }
    except Exception as e:
        payload = {
            'error': str(e)
        }
    return JsonResponse(payload)


@csrf_exempt
def ActiveAPI(request):
    try:
        query_set = StockConfig.objects.filter(is_active=True).values()
        payload = {
            'data': list(query_set)
        }
    except Exception as e:
        payload = {
            'error': str(e)
        }
    return JsonResponse(payload)