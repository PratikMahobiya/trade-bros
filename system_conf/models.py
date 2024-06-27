from django.db import models

# Create your models here.
class Configuration(models.Model):
    amount = models.BigIntegerField(verbose_name='AMOUNT', default=4000)
    place_order = models.BooleanField(default=False, verbose_name="Activate Order Placement")
    buy_market_order = models.BooleanField(default=False)
    sell_market_order = models.BooleanField(default=True)
    daily_fixed_stoploss = models.FloatField(verbose_name='Daily Fixed SL', default=0)
    daily_max_profit = models.FloatField(verbose_name='Daily Max-Profit', default=0)
    daily_max_profit_time = models.DateTimeField(null=True, blank=True)
    daily_max_loss = models.FloatField(verbose_name='Daily Max-Loss', default=0)
    daily_max_loss_time = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"