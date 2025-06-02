from task import UpdateHoliday
from django.contrib import admin
from helper.common import colour
from import_export.admin import ExportActionMixin
from admin_extra_buttons.api import ExtraButtonsMixin, button
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from system_conf.models import Configuration, OIChange, Symbol, Holiday

# Register your models here.
@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ('product', 'amount', 'open_position', 'stoploss', 'target', 'fixed_target', 'trail_stoploss_by', 'is_active')


@admin.register(Holiday)
class HolidayAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ('holiday', 'day', 'date', 'is_active')
    
    def get_ordering(self, request):
        return ['date']

    @button(change_form=True,
        html_attrs={'style': 'background-color:#F1502F;color:black'})
    def UpdateHoliday(self, request):
        self.message_user(request, 'Holiday Update called')
        UpdateHoliday()
        self.message_user(request, 'Holiday Update Done')

        return HttpResponseRedirectToReferrer(request)


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    list_display = ('exchange', 'symbol', 'percentchange_', 'ltp', 'name', 'pivot', 'r1', 'r2', 'r3', 's1', 's2', 's3', 'week_pivot', 'week_r1', 'week_r2', 'week_r3', 'week_s1', 'week_s2', 'week_s3', 'month_pivot', 'month_r1', 'month_r2', 'month_r3', 'month_s1', 'month_s2', 'month_s3', 'weekhigh52', 'weeklow52', 'nifty50', 'nifty100', 'nifty200', 'midcpnifty50', 'midcpnifty100', 'midcpnifty150', 'smallcpnifty50', 'smallcpnifty100', 'smallcpnifty250', 'expiry', 'strike', 'token', 'volume', 'valuechange', 'oi', 'lot', 'fno', 'product', 'is_active')
    list_filter = ('product', 'exchange', 'fno', 'nifty50', 'nifty100', 'nifty200', 'midcpnifty50', 'midcpnifty100', 'midcpnifty150', 'smallcpnifty50', 'smallcpnifty100', 'smallcpnifty250')
    search_fields = ['name', 'symbol', 'token']

    def get_ordering(self, request):
        return ['product', '-nifty200', '-nifty100', '-nifty50', '-midcpnifty150', '-midcpnifty100', '-midcpnifty50', '-smallcpnifty250', '-smallcpnifty100', '-smallcpnifty50', '-percentchange']
    
    def percentchange_(self, obj):
        return colour(obj.percentchange)
    percentchange_.short_description = 'Change(%)'


@admin.register(OIChange)
class OIChangeAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('name', 'oi_', 'oi_915', 'oi_930', 'oi_945', 'oi_10', 'oi_1015', 'oi_1030', 'oi_1045', 'oi_11', 'oi_1115', 'oi_1130', 'oi_1145', 'oi_12', 'oi_1215', 'oi_1230', 'oi_1245', 'oi_13', 'oi_1315', 'oi_1330', 'oi_1345', 'oi_14', 'oi_1415', 'oi_1430', 'oi_1445', 'oi_15', 'oi_1515', 'oi_1530', 'is_active')
    search_fields = ['name', ]
    list_per_page = 1000
    
    def get_ordering(self, request):
        return ['-oi']

    def oi_(self, obj):
        return colour(obj.oi)
    oi_.short_description = 'OI(%)'
