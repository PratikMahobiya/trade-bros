from django.contrib import admin
from system_conf.models import Configuration

# Register your models here.
@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ('amount', 'daily_fixed_stoploss', 'place_order', 'buy_market_order','sell_market_order', 'daily_max_profit', 'daily_max_profit_time', 'daily_max_loss', 'daily_max_loss_time', 'is_active')