from time import sleep
from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Count, Sum
from admin_extra_buttons.api import ExtraButtonsMixin, button
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer

from admin_extra_buttons.api import ExtraButtonsMixin
from dashboard.models import Status, DailyStatus
from helper.common import colour
from helper.connection import AngelOne, Fyers
from option.models import StockConfig, Transaction, Index
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from system_conf.models import Configuration


# Register your models here.
def up_model(ltp, price):
    diff = ltp - price
    profit = round(((diff/price) * 100), 2)
    if profit < 0:
        return format_html('<strong style="color:Red;">{}</strong>', profit)
    return format_html('<strong style="color:Green;">{}</strong>', profit)


@admin.register(DailyStatus)
class DailyStatusAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    actions = None
    list_display = ['model_', 'p_l', 'entry', 'active', 'exit', 'max_profit', 'max_profit_time', 'max_loss', 'max_loss_time']

    def has_add_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        return Configuration.objects.all()
    
    def model_(self, obj):
        return 'Sataru-Gojo'
    
    def entry(self, obj):
        return len(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='ENTRY'))
    
    def exit(self, obj):
        return len(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT'))
    
    def active(self, obj):
        return len(StockConfig.objects.filter(is_active=True))

    def p_l(self, obj):
        return colour(round(sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT').values_list('profit', flat=True)), 2))
    p_l.short_description = 'Profit(%)'

    def max_profit(self, obj):
        return colour(obj.daily_max_profit)
    max_profit.short_description = 'Max Profit(%)'
    
    def max_profit_time(self, obj):
        return obj.daily_max_profit_time
    max_profit_time.short_description = 'Max P(%) Time'
    
    def max_loss(self, obj):
        return colour(obj.daily_max_loss)
    max_loss.short_description = 'Max Loss(%)'
    
    def max_loss_time(self, obj):
        return obj.daily_max_loss_time
    max_loss_time.short_description = 'Max L(%) Time'

    @button(change_form=True,
            html_attrs={'style': 'background-color:#FFFD29;color:black'})
    def GOJO_TODAY(self, request):
        daily_sl_obj = Configuration.objects.all()[0]
        if (sum(Transaction.objects.filter(date__date=datetime.now(tz=ZoneInfo("Asia/Kolkata")).date(), indicate='EXIT').values_list('profit', flat=True)) < -daily_sl_obj.daily_fixed_stoploss):
            self.message_user(request, f'Trading Stopped because Daily Stoploss Hitted {daily_sl_obj.daily_fixed_stoploss} % at {(daily_sl_obj.daily_max_loss_time + timedelta(hours=5, minutes=30)).strftime("%T")}', level=messages.ERROR)
        now = datetime.now()
        transaction_list = Transaction.objects.filter(date__date = datetime.now().date(), indicate='EXIT', is_active=True).values('index').annotate(profit=Sum('profit'), trade=Count('indicate'))
        index_wise_str = ''
        for trans_obj in transaction_list:
            index_obj = Index.objects.get(index=trans_obj['index'])
            days_difference = (index_obj.expiry_date - now.date()).days
            if index_obj.expiry_date == now.date() or ((index_obj.expiry_date - now.date()).days == 7):
                daily_target = index_obj.fixed_target + 5
            elif index_obj.index in ['BANKNIFTY'] and days_difference in [6]:
                daily_target = 23
            elif index_obj.index in ['FINNIFTY'] and days_difference in [6, 5]:
                daily_target = 15
            else:
                daily_target = round(index_obj.fixed_target/(days_difference+1), 2)
            if round(trans_obj['profit'], 2) > daily_target:
                target_status = "Achived "
            else:
                target_status = "Yet to achive "
            index_wise_str = trans_obj['index'] + ": P/L of " + str(round(trans_obj['profit'], 2)) + '%' + ' : on ' + str(trans_obj['trade']) + " trades, target status: " + target_status + str(daily_target) + '%'
            if round(trans_obj['profit'], 2) > daily_target:
                self.message_user(request, index_wise_str, level=messages.INFO)
            elif now.time() > time(15, 15, 00) and round(trans_obj['profit'], 2) < daily_target:
                if round(trans_obj['profit'], 2) > 0:
                    index_wise_str = index_wise_str.replace(target_status, 'Achived ')
                    self.message_user(request, index_wise_str, level=messages.INFO)
                else:
                    index_wise_str = index_wise_str.replace(target_status, 'Failed to achive ')
                    self.message_user(request, index_wise_str, level=messages.ERROR)
            else:
                self.message_user(request, index_wise_str, level=messages.WARNING)

        if index_wise_str == '':
            index_wise_str = 'No Trades.'
            self.message_user(request, index_wise_str)
        return HttpResponseRedirectToReferrer(request)

    @button(change_form=True,
            html_attrs={'style': 'background-color:#15FBF1;color:black'})
    def GOJO_TILL_NOW(self, request):
        total_entry = Transaction.objects.filter(indicate='EXIT', is_active=True).order_by('date').count()
        date_ = Transaction.objects.filter(indicate='EXIT', is_active=True).order_by('date')[0].date.strftime("%d %B, %Y")
        accuracy = round((len(Transaction.objects.filter(profit__gte=0, indicate='EXIT', is_active=True))/total_entry) * 100, 2)
        return_1 = round(sum(Transaction.objects.filter(indicate='EXIT', is_active=True).values_list('profit', flat=True)), 2)
        self.message_user(request, f'Sataru-Gojo: {return_1} % --- Gained From: {date_}')
        self.message_user(request, f'{accuracy} % Accuracy on {total_entry} Trades.')
        return HttpResponseRedirectToReferrer(request)

    @button(change_form=True,
            html_attrs={'style': 'background-color:#ee8623;color:black'})
    def GOJO_LAST_MONTH(self, request):
        # Calculate the first day of the next month
        month_first_day = datetime(datetime.now().year, datetime.now().month, 1)
        total_entry = Transaction.objects.filter(indicate='EXIT', created_at__gte=month_first_day,  is_active=True).order_by('date').count()
        date_ = month_first_day.strftime("%d %B, %Y")
        accuracy = round((len(Transaction.objects.filter(profit__gte=0, indicate='EXIT', created_at__gte=month_first_day, is_active=True))/total_entry) * 100, 2)
        return_1 = round(sum(Transaction.objects.filter(indicate='EXIT', created_at__gte=month_first_day, is_active=True).values_list('profit', flat=True)), 2)
        self.message_user(request, f'Sataru-Gojo: {return_1} % --- Gained Last Month from: {date_}')
        self.message_user(request, f'{accuracy} % Accuracy on {total_entry} Trades.')
        return HttpResponseRedirectToReferrer(request)


@admin.register(Status)
class StatusAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    actions = None
    list_display = ('entry_time', 'index', 'current', 'max_p', 'max_l_s', 'highest_price', 'price', 'fixed_target', 'lot', 'order_id', 'order_status', 'mode', 'strike', 'target', 'stoploss', 'tr_hit', 'trailing_sl')

    def has_add_permission(self, request, obj=None):
        return False
    
    def index(self, obj):
        return f"{obj.symbol.index.index[:4]}_{obj.symbol.symbol[-5:]}_{obj.mode}" if "EX" not in obj.symbol.index.index else f"{obj.symbol.index.index[0]}{obj.symbol.index.index[3:6]}_{obj.symbol.symbol[-5:]}_{obj.mode}"
    
    def strike(self, obj):
        return obj.symbol.strike_price
    
    def entry_time(self, obj):
        return (obj.created_at + timedelta(hours=5, minutes=30)).strftime("%-I:%-M:%-S %p")
    entry_time.short_description = 'Time'

    def max_p(self, obj):
        return colour(obj.max)
    max_p.short_description = 'Max-P%'
    
    def max_l_s(self, obj):
        return colour(obj.max_l)
    max_l_s.short_description = 'Max-L%'

    def current(self, obj):
        ltp = Fyers(
            'Fyers-Pratik').quotes({"symbols": f'{obj.symbol}{obj.mode}'})['d'][0]['v']['lp']
        sleep(0.2)
        return up_model(ltp, obj.price)
        # return up_model(obj.curr_price, obj.price)
