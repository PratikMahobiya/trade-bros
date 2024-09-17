from django.db import models

# Create your models here.
class Configuration(models.Model):
    product = models.CharField(default='equity', max_length=255, unique=True, verbose_name="Product")
    place_order = models.BooleanField(default=False, verbose_name="Place Order")
    amount = models.FloatField(default=10000, verbose_name="Amount")
    open_position = models.BigIntegerField(default=10, verbose_name='Open Position')
    stoploss = models.FloatField(default=3, verbose_name="Stoploss(%)")
    target = models.FloatField(default=4, verbose_name="Target(%)")
    fixed_target = models.FloatField(default=4, verbose_name="Fixed TR(%)")
    trail_stoploss_by = models.FloatField(default=5, verbose_name="Trail Stoploss By(%)")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}-{self.product}"


class Symbol(models.Model):
  product = models.CharField(default='equity', max_length=255, unique=True, verbose_name="Product")
  name = models.CharField(max_length=100, verbose_name='Name', unique=True)
  symbol = models.CharField(max_length=100, verbose_name='Symbol', unique=True)
  exchange = models.CharField(max_length=100, verbose_name='Exchange', unique=True)
  strike = models.BigIntegerField(verbose_name='Strike', null=True, blank=True)
  token = models.CharField(max_length=100, verbose_name='Token', null=True, blank=True)
  expiry_date = models.DateField(verbose_name='Expiry Date', null=True, blank=True)
  lot = models.BigIntegerField(verbose_name='Lots', null=True, blank=True)

  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
      return f"{self.id}-{self.symbol}"