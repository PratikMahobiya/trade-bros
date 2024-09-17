from django.contrib import admin
from import_export.admin import ExportActionMixin

from helper.common import colour
from stock.models import StockConfig, Transaction

# Register your models here.
@admin.register(StockConfig)
class StockConfigAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'mode', 'symbol__name', 'ltp', 'tr_hit', 'trailing_sl', 'max', 'max_l', 'price', 'target', 'stoploss', 'fixed_target', 'highest_price', 'symbol__symbol', 'lot', 'order_status', 'is_active')
    search_fields = ['symbol', ]

    def get_ordering(self, request):
        return ['-created_at']


@admin.register(Transaction)
class TransactionAdmin(ExportActionMixin, admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('product', 'symbol', 'date', 'indicate', 'type', 'p_l', 'max_p', 'max_l_s', 'top_p', 'price', 'fixed_target', 'stoploss', 'target', 'lot', 'order_id', 'order_status', 'mode')
    search_fields = ['symbol', ]
    list_filter = ('indicate', 'date', 'mode')
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