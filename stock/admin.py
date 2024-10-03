from datetime import timedelta
from django.contrib import admin
from import_export.admin import ExportActionMixin
from admin_extra_buttons.api import ExtraButtonsMixin, button
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer

from helper.common import colour, up_model
from stock.models import StockConfig, Transaction, Status

# Register your models here.
@admin.register(Status)
class StatusAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    actions = None
    list_display = ('entry_time', 'name_', 'current', 'max_p', 'max_l_s', 'ltp', 'fixed_target', 'price', 'stoploss', 'trailing_sl', 'target', 'highest_price', 'orderid', 'order_status', 'lot', 'tr_hit', 'mode', 'product')

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return self.model.objects.all()
    
    def product(self, obj):
        return f"{obj.symbol.product}"
    product.short_description = 'Product'

    def name_(self, obj):
        if obj.symbol.product == 'future':
            return f"{obj.symbol.name}-{obj.symbol.strike}-{obj.symbol.symbol[-2:]}"
        else:
            return f"{obj.symbol.symbol}"
    name_.short_description = 'Name'
    
    def entry_time(self, obj):
        return (obj.created_at + timedelta(hours=5, minutes=30)).strftime("%d/%m/%y %-I:%-M:%-S %p")
    entry_time.short_description = 'Time'

    def max_p(self, obj):
        return colour(round(obj.max, 2))
    max_p.short_description = 'Max-P%'
    
    def max_l_s(self, obj):
        return colour(round(obj.max_l, 2))
    max_l_s.short_description = 'Max-L%'
    
    def orderid(self, obj):
        return obj.order_id[-7:]
    orderid.short_description = 'Order ID'

    def current(self, obj):
        return up_model(obj, obj.ltp)

    @button(change_form=True,
            html_attrs={'style': 'background-color:#15FBF1;color:black'})
    def EQUITY_STATUS(self, request):
        equity_total_exit = Transaction.objects.filter(product='equity', indicate='EXIT', is_active=True).order_by('date').count()
        equity_total_entry = Transaction.objects.filter(product='equity', indicate='ENTRY', is_active=True).order_by('date').count()
        equity_accuracy = round((len(Transaction.objects.filter(product='equity', profit__gte=0, indicate='EXIT', is_active=True))/equity_total_exit) * 100, 2) if equity_total_exit != 0 else 0
        equity_return_1 = round(sum(Transaction.objects.filter(product='equity', indicate='EXIT', is_active=True).values_list('profit', flat=True)), 2)

        self.message_user(request, f'Total Equity Entry: {equity_total_entry}, Exit: {equity_total_exit}.')
        self.message_user(request, f'Equity: {equity_accuracy} % Accuracy on {equity_total_exit} Trades.')
        self.message_user(request, f'--- Equity Till Now: {equity_return_1} % ---')
        return HttpResponseRedirectToReferrer(request)


    @button(change_form=True,
            html_attrs={'style': 'background-color:#15FBF1;color:black'})
    def FUTURE_STATUS(self, request):
        future_total_exit = Transaction.objects.filter(product='future', indicate='EXIT', is_active=True).order_by('date').count()
        future_total_entry = Transaction.objects.filter(product='future', indicate='ENTRY', is_active=True).order_by('date').count()
        future_accuracy = round((len(Transaction.objects.filter(product='future', profit__gte=0, indicate='EXIT', is_active=True))/future_total_exit) * 100, 2) if future_total_exit != 0 else 0
        future_return_1 = round(sum(Transaction.objects.filter(product='future', indicate='EXIT', is_active=True).values_list('profit', flat=True)), 2)
        self.message_user(request, f'Total Future Entry: {future_total_entry}, Exit: {future_total_exit}.')
        self.message_user(request, f'Future: {future_accuracy} % Accuracy on {future_total_exit} Trades.')
        self.message_user(request, f'--- Future Till Now: {future_return_1} % ---')
        return HttpResponseRedirectToReferrer(request)


@admin.register(StockConfig)
class StockConfigAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'mode', 'symbol__name', 'ltp', 'tr_hit', 'trailing_sl', 'max', 'max_l', 'price', 'target', 'stoploss', 'fixed_target', 'highest_price', 'symbol__symbol', 'lot', 'order_status', 'is_active')
    search_fields = ['symbol', ]

    def get_ordering(self, request):
        return ['-created_at']


@admin.register(Transaction)
class TransactionAdmin(ExportActionMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('product', 'symbol', 'date', 'indicate', 'type', 'p_l', 'max_p', 'max_l_s', 'top_p', 'price', 'fixed_target', 'stoploss', 'target', 'lot', 'order_id', 'order_status', 'name', 'mode')
    search_fields = ['symbol', ]
    list_filter = ('indicate', 'date', 'mode', 'name')
    list_per_page = 20

    def get_ordering(self, request):
        return ['-date']
    
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
