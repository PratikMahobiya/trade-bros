from datetime import timedelta
from django.contrib import admin
from logs.models import Log
from admin_extra_buttons.api import ExtraButtonsMixin, button
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer

# Register your models here.
@admin.register(Log)
class LogAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ('log_name','log_desc', 'error')
    readonly_fields=('log_name','log_desc', 'error')
    search_fields = ['log_name', 'log_desc']
    list_filter = ('error',)