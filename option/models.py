from django.db import models

# Create your models here.
class Keys(models.Model):
  broker_name = models.CharField(max_length=200, verbose_name='Broker name')
  username = models.CharField(max_length=200, unique=True, verbose_name='UserName', default='please_enter_user_name')
  api_key = models.TextField(verbose_name='Api Key', null=True, blank=True)
  secret_key = models.TextField(verbose_name='Api Secret Key', null=True, blank=True)
  user_id = models.CharField(max_length=100, verbose_name='Account Id', null=True, blank=True)
  user_password = models.CharField(max_length=100, verbose_name='Account Password', null=True, blank=True)
  user_pin = models.CharField(max_length=50, verbose_name='Pin', null=True, blank=True, default='please_enter_user_pin')
  access_token = models.TextField(verbose_name='Access Token', null=True, blank=True, default='please_enter_user_accesstoken')

  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
      return f"{self.broker_name}-{self.username}"


class Index(models.Model):
  index = models.CharField(max_length=200, verbose_name='Index')
  index_symbol = models.CharField(max_length=200, verbose_name='Index Symbol', blank=True)
  target = models.FloatField(verbose_name='Target(%)', default=9)
  stoploss = models.FloatField(verbose_name='Stoploss(%)', default=30)
  fixed_target = models.FloatField(verbose_name='Fixed Target(%)', default=30)
  min_price = models.FloatField(verbose_name='Min Price', default=0)
  max_price = models.FloatField(verbose_name='Max Price', default=200)
  trailing_target = models.BooleanField(verbose_name='Trailing Target', default=False)
  expiry_date = models.DateField(verbose_name='Expiry Date', null=True, blank=True)
  chain_strike_price_diff = models.FloatField(verbose_name='Chain Strike Price Difference', default=0)
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
  
  def __str__(self):
      return self.index


class DailyRecord(models.Model):
  date = models.DateField(verbose_name='DATE', null=True, blank=True)
  day = models.CharField(max_length=100, verbose_name='DAY', null=True, blank=True)
  total_entry = models.BigIntegerField(verbose_name='Total Entry', default=0)
  p_l = models.FloatField(verbose_name='P/L(%)', default=0)
  daily_max_profit = models.FloatField(verbose_name='Daily Max-Profit', default=0)
  daily_max_profit_time = models.DateTimeField(null=True, blank=True)
  daily_max_loss = models.FloatField(verbose_name='Daily Max-Loss', default=0)
  daily_max_loss_time = models.DateTimeField(null=True, blank=True)

  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
      return f"{self.id}"


class OptionSymbol(models.Model):
  index = models.ForeignKey(Index, on_delete=models.CASCADE, verbose_name='Index', null=True)
  strike_price = models.BigIntegerField(verbose_name='Strike Price')
  symbol = models.CharField(max_length=100, verbose_name='SYMBOL', unique=True)
  call_token = models.CharField(max_length=100, verbose_name='Angel One Call TOKEN')
  put_token = models.CharField(max_length=100, verbose_name='Angel One Put TOKEN')
  call_angel_symbol = models.CharField(max_length=100, verbose_name='Angel One Call Symbol', default='NONE')
  put_angel_symbol = models.CharField(max_length=100, verbose_name='Angel One Put Symbol', default='NONE')
  lot = models.BigIntegerField(verbose_name='Lots', default=0)

  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  def __str__(self):
      return self.symbol


class StockConfig(models.Model):
  MODES = [('CE', "Call"),
           ('PE', "Put"),
           ('none', "N/A")]
  symbol = models.ForeignKey(OptionSymbol, on_delete=models.CASCADE)
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
    return str(self.id)


class Transaction(models.Model):
  MODES = [('CE', "Call"),
           ('PE', "Put"),
           ('none', "N/A")]
  mode = models.CharField(max_length=50, choices=MODES,verbose_name='MODE', default='none')
  index = models.CharField(max_length=200, verbose_name='INDEX')
  symbol = models.CharField(max_length=200, verbose_name='SYMBOL')
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
      return str(self.id) + self.symbol