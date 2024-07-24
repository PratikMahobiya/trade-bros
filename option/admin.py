from import_export.admin import ExportActionMixin
from admin_extra_buttons.api import ExtraButtonsMixin, button
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer

from django.contrib import admin
from option.models import DailyRecord, Index, Keys, OptionSymbol, StockConfig, Transaction
from helper.common import colour

# Register your models here.
# Register your models here.
@admin.register(Keys)
class KeyAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('broker_name', 'username', 'api_key', 'secret_key',
                    'user_id', 'user_password', 'user_pin', 'is_active')


@admin.register(Index)
class IndexAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('index', 'index_symbol', 'pivot', 'r1', 'r2', 'r3', 's1', 's2', 's3', 'target', 'stoploss', 'fixed_target', 'min_price', 'max_price', 'expiry_date', 'trailing_target', 'chain_strike_price_diff', 'is_active')


@admin.register(DailyRecord)
class DailyRecordAdmin(ExportActionMixin, ExtraButtonsMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'p_l_s', 'total_entry', 'max_profit', 'daily_max_profit_time', 'max_loss', 'daily_max_loss_time', 'day', 'is_active')
    list_filter = ('day',)
    list_per_page = 20

    def get_ordering(self, request):
        return ['-created_at']

    def p_l_s(self, obj):
        return colour(obj.p_l)
    p_l_s.short_description = 'P/L(%)'

    def max_profit(self, obj):
        return colour(obj.daily_max_profit)
    max_profit.short_description = 'Max Profit(%)'
    
    def max_loss(self, obj):
        return colour(obj.daily_max_loss)
    max_loss.short_description = 'Max Loss(%)'
 
    @button(change_form=True,
            html_attrs={'style': 'background-color:#2937ff;color:white'})
    def PROFIT_LOSS_UPDATE(self, request):
        self.message_user(request, 'P/L UPDATE Called')
        daily_record_list = DailyRecord.objects.filter(is_active=True)
        for obj in daily_record_list:
            transaction_list = Transaction.objects.filter(date__date=obj.date, indicate='EXIT').order_by('date')
            p_l = 0
            obj.daily_max_profit = 0
            obj.daily_max_loss = 0
            obj.total_entry = len(transaction_list)
            for t_obj in transaction_list:
                p_l += t_obj.profit
                if p_l > obj.daily_max_profit:
                    obj.daily_max_profit = round(p_l, 2)
                    obj.daily_max_profit_time = t_obj.date
                elif p_l < obj.daily_max_loss:
                    obj.daily_max_loss = round(p_l, 2)
                    obj.daily_max_loss_time = t_obj.date
            obj.p_l = round(p_l, 2)
            obj.save()
        self.message_user(request, 'P/L UPDATE Done')
        return HttpResponseRedirectToReferrer(request)


@admin.register(OptionSymbol)
class OptionSymbolAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('index', 'strike_price', 'symbol', 'call_token', 'put_token', 'call_angel_symbol', 'put_angel_symbol', 'lot', 'is_active')
    search_fields = ['symbol', 'index']
    list_filter = ['index', ]
    list_per_page = 20

    def get_ordering(self, request):
        return ['-created_at']

@admin.register(StockConfig)
class StockConfigAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'mode', 'symbol', 'ltp', 'tr_hit', 'trailing_sl', 'max', 'max_l', 'price', 'target', 'stoploss', 'fixed_target', 'highest_price', 'lot', 'order_status', 'is_active')
    search_fields = ['symbol', ]

    def get_ordering(self, request):
        return ['-created_at']
    
    def index(self, obj):
        return obj.symbol.index
    

@admin.register(Transaction)
class TransactionAdmin(ExportActionMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('index_', 'date', 'indicate', 'type', 'p_l', 'max_p', 'max_l_s', 'top_p', 'price', 'fixed_target', 'lot', 'order_id', 'order_status', 'mode', 'strike', 'target', 'stoploss')
    search_fields = ['symbol', ]
    list_filter = ('index', 'indicate', 'date', 'mode')
    list_per_page = 20

    def get_ordering(self, request):
        return ['-date']
    
    def strike(self, obj):
        return obj.symbol[-7:-2]
    
    def index_(self, obj):
        return f"{obj.index[:4]}_{obj.symbol[-7:-2]}_{obj.symbol[-2:]}" if "EX" not in obj.index else f"{obj.index[0]}{obj.index[3:6]}_{obj.symbol[-7:-2]}_{obj.symbol[-2:]}"

    def top_p(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return obj.highest_price
    top_p.short_description = 'Top Price'

    def max_p(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return colour(obj.max)
    max_p.short_description = 'Max-P%'
    
    def max_l_s(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return colour(obj.max_l)
    max_l_s.short_description = 'Max-L%'
    
    def p_l(self, obj):
        if obj.indicate == "ENTRY":
            return ''
        else:
            return colour(obj.profit)
    p_l.short_description = 'Profit-%'