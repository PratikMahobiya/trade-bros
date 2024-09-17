from django.contrib import admin
from system_conf.models import Configuration, Symbol
from admin_extra_buttons.api import ExtraButtonsMixin, button
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer

from task import BrokerConnection, Equity_BreakOut_1, SymbolSetup

# Register your models here.
@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ('product', 'place_order', 'open_position', 'amount', 'stoploss', 'target', 'fixed_target', 'trail_stoploss_by', 'is_active')


@admin.register(Symbol)
class SymbolAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ('product', 'name', 'symbol', 'exchange', 'token', 'expiry', 'strike', 'lot', 'is_active')
    list_filter = ('product',)
    search_fields = ['name', 'symbol']

    @button(change_form=True,
            html_attrs={'style': 'background-color:#F1502F;color:black'})
    def Symbol_Setup(self, request):
        self.message_user(request, 'Symbol Setup called')
        SymbolSetup()
        self.message_user(request, 'Symbol Setup Done')
        return HttpResponseRedirectToReferrer(request)
    
    @button(change_form=True,
            html_attrs={'style': 'background-color:#F1502F;color:black'})
    def Equity_BreakOut_1(self, request):
        self.message_user(request, 'Equity BreakOut 1 called')
        Equity_BreakOut_1()
        self.message_user(request, 'Equity BreakOut 1 Done')
        return HttpResponseRedirectToReferrer(request)
    
    @button(change_form=True,
            html_attrs={'style': 'background-color:#F1502F;color:black'})
    def Connect(self, request):
        self.message_user(request, 'Connect called')
        BrokerConnection()
        self.message_user(request, 'Connect Done')
        return HttpResponseRedirectToReferrer(request)