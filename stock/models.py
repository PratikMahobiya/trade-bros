from django.db import models

from system_conf.models import Symbol

# Create your models here.
class StockConfig(models.Model):
    MODES = [('CE', "Call"),
            ('PE', "Put"),
            ('none', "N/A")]
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    mode = models.CharField(max_length=50, choices=MODES, verbose_name='MODE', default='none')
    price = models.FloatField(verbose_name='PRICE', default=0)
    stoploss = models.FloatField(verbose_name='STOPLOSS', default=0)
    target = models.FloatField(verbose_name='TARGET', default=0)
    fixed_target = models.FloatField(verbose_name='Fixed Target', blank=True, null=True, default=0)
    max = models.FloatField(verbose_name='MAX GAIN', default=0)
    max_l = models.FloatField(verbose_name='MAX LOSS', default=0)
    highest_price = models.FloatField(verbose_name='HIGHEST PRICE', default=0)
    lot = models.FloatField(verbose_name='Lots', default=0)
    order_id = models.CharField(max_length=255, verbose_name='ORDER ID', blank=True, null=True, default='0')
    order_status = models.TextField( verbose_name='ORDER STATUS', default='NONE')
    tr_hit = models.BooleanField(verbose_name='Target Hit', default=False)
    trailing_sl = models.FloatField(verbose_name='Trailing SL', default=0)
    ltp = models.FloatField(verbose_name='Ltp', blank=True, null=True, default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}-{self.symbol}"


class Transaction(models.Model):
    MODES = [('CE', "Call"),
            ('PE', "Put"),
            ('none', "N/A")]
    product = models.CharField(default='equity', max_length=255, verbose_name='Product')
    symbol = models.CharField(max_length=255, verbose_name='Symbol')
    mode = models.CharField(max_length=50, choices=MODES,verbose_name='MODE', default='none')
    indicate = models.CharField(max_length=50, verbose_name='INDICATE')
    type = models.CharField(max_length=50, verbose_name='TYPE')
    date = models.DateTimeField(auto_now_add=True)
    price = models.FloatField(verbose_name='PRICE')
    stoploss = models.FloatField(verbose_name='STOPLOSS')
    target = models.FloatField(verbose_name='TARGET')
    fixed_target = models.FloatField(verbose_name='Fixed Target', blank=True, null=True, default=0)
    profit = models.FloatField(verbose_name='PROFIT (%)', blank=True, null=True, default=0)
    max = models.FloatField(verbose_name='MAX-P (%)', blank=True, null=True, default=0)
    max_l = models.FloatField(verbose_name='MAX-L (%)', default=0)
    highest_price = models.FloatField(verbose_name='HIGHEST PRICE', default=0)
    order_id = models.CharField(max_length=255, verbose_name='ORDER ID', blank=True, null=True, default='0')
    order_status = models.TextField(verbose_name='ORDER STATUS')
    lot = models.FloatField(verbose_name='LOT')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}-{self.product}-{self.symbol}"