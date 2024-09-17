from django.contrib import admin
from system_conf.models import Configuration, Symbol
from admin_extra_buttons.api import ExtraButtonsMixin, button
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer

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
