from django.db import models

# Create your models here.
class Log(models.Model):
    log_name = models.CharField(max_length=255, unique=True, verbose_name="Log Name")
    log_desc = models.TextField(verbose_name="Log Desc")
    error = models.BooleanField(default=False, verbose_name="Error")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.log_name