from django.db import models

# Create your models here.
class Configuration(models.Model):
    product = models.CharField(default='equity', max_length=255, unique=True, verbose_name="Product")
    amount = models.FloatField(default=10000, verbose_name="Amount")
    open_position = models.BigIntegerField(default=10, verbose_name='Open Position')
    stoploss = models.FloatField(default=3, verbose_name="Stoploss(%)")
    target = models.FloatField(default=4, verbose_name="Target(%)")
    fixed_target = models.FloatField(default=4, verbose_name="Fixed TR(%)")
    trail_stoploss_by = models.FloatField(default=5, verbose_name="Trail Stoploss By(%)")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
       indexes = [
            models.Index(fields=['product',]),
            ]

    def __str__(self):
        return f"{self.id}-{self.product}"


class Symbol(models.Model):
    product = models.CharField(default='equity', max_length=255, verbose_name="Product")
    name = models.CharField(max_length=100, verbose_name='Name')
    symbol = models.CharField(max_length=100, verbose_name='Symbol', unique=True)
    exchange = models.CharField(max_length=100, verbose_name='Exchange')
    strike = models.BigIntegerField(verbose_name='Strike', null=True, blank=True)
    token = models.CharField(max_length=100, verbose_name='Token', null=True, blank=True, unique=True)
    expiry = models.DateField(verbose_name='Expiry', null=True, blank=True)
    lot = models.BigIntegerField(verbose_name='Lots', null=True, blank=True)
    fno = models.BooleanField(verbose_name='FNO', default=False)
    volume = models.FloatField(default=0, verbose_name="Volume")
    oi = models.FloatField(default=0, verbose_name="Open Interest")
    percentchange = models.FloatField(default=0, verbose_name="Change(%)")
    valuechange = models.FloatField(default=0, verbose_name="Change(Value)")
    ltp = models.FloatField(default=0, verbose_name="LTP")
    weekhigh52 = models.FloatField(default=0, verbose_name="52 Week High")
    weeklow52 = models.FloatField(default=0, verbose_name="52 Week Low")
    nifty50 = models.BooleanField(default=False, verbose_name='Nifty50')
    nifty100 = models.BooleanField(default=False, verbose_name='Nifty100')
    nifty200 = models.BooleanField(default=False, verbose_name='Nifty200')
    midcpnifty50 = models.BooleanField(default=False, verbose_name='MidCP50')
    midcpnifty100 = models.BooleanField(default=False, verbose_name='MidCP100')
    midcpnifty150 = models.BooleanField(default=False, verbose_name='MidCP150')
    smallcpnifty50 = models.BooleanField(default=False, verbose_name='SmallCP50')
    smallcpnifty100 = models.BooleanField(default=False, verbose_name='SmallCP100')
    smallcpnifty250 = models.BooleanField(default=False, verbose_name='SmallCP250')
    pivot = models.FloatField(verbose_name='Pivot', default=0)
    r1 = models.FloatField(verbose_name='R1', default=0)
    s1 = models.FloatField(verbose_name='S1', default=0)
    r2 = models.FloatField(verbose_name='R2', default=0)
    s2 = models.FloatField(verbose_name='S2', default=0)
    r3 = models.FloatField(verbose_name='R3', default=0)
    s3 = models.FloatField(verbose_name='S3', default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
       indexes = [
            models.Index(fields=['-fno',]),
            models.Index(fields=['exchange',]),
            models.Index(fields=['product',]),
            models.Index(fields=['-nifty50',]),
            models.Index(fields=['-nifty100',]),
            models.Index(fields=['-nifty200',]),
            models.Index(fields=['-midcpnifty50',]),
            models.Index(fields=['-midcpnifty100',]),
            models.Index(fields=['-midcpnifty150',]),
            models.Index(fields=['-smallcpnifty50',]),
            models.Index(fields=['-smallcpnifty100',]),
            models.Index(fields=['-smallcpnifty250',]),
            ]

    def __str__(self):
        return f"{self.id}-{self.symbol}"