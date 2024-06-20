from django.db import models
from option.models import StockConfig

# Create your models here.
class DailyStatus(models.Model):
    class Meta:
        verbose_name = "Daily Status"
        verbose_name_plural = "Daily Status"


class Status(StockConfig):
    class Meta:
        proxy = True
        verbose_name = "Status"
        verbose_name_plural = "Status"