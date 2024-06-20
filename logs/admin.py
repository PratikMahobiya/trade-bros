from datetime import timedelta
from django.contrib import admin
from logs.models import Log
from admin_extra_buttons.api import ExtraButtonsMixin, button
from admin_extra_buttons.utils import HttpResponseRedirectToReferrer
from tasks import PivotUpdate, BasicSetupJob, DeleteLogs, FyersSetup, NotifyUsers, CallPutAction, Minute1

# Register your models here.
@admin.register(Log)
class LogAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    date_hierarchy = "created_at"
    list_display = ('log_name','log_desc', 'error')
    readonly_fields=('log_name','log_desc', 'error')
    search_fields = ['log_name', 'log_desc']
    list_filter = ('error',)

    @button(change_form=True,
            html_attrs={'style': 'background-color:#F1502F;color:black'})
    def Pivot_Update(self, request):
        self.message_user(request, 'BackUp called')
        PivotUpdate()
        self.message_user(request, 'BackUp Done')
        return HttpResponseRedirectToReferrer(request)

    @button(change_form=True,
            html_attrs={'style': 'background-color:#33FFE6;color:black'})
    def Fyers_Connection(self, request):
        self.message_user(request, 'Fyers-Connection called')
        FyersSetup()
        self.message_user(request, 'Fyers-Connection Done')
        return HttpResponseRedirectToReferrer(request)

    @button(change_form=True,
            html_attrs={'style': 'background-color:#7DFF33;color:black'})
    def Basic_Setup(self, request):
        self.message_user(request, 'Basic-Setup called')
        BasicSetupJob()
        self.message_user(request, 'Basic-Setup Done')
        return HttpResponseRedirectToReferrer(request)

    @button(change_form=True,
            html_attrs={'style': 'background-color:#FF3364;color:black'})
    def Delete_Logs(self, request):
        self.message_user(request, 'Delete-Logs called')
        DeleteLogs()
        self.message_user(request, 'Delete-Logs Done')
        return HttpResponseRedirectToReferrer(request)
    
    @button(change_form=True,
            html_attrs={'style': 'background-color:#FF3364;color:black'})
    def CALL_PUT_ACTION(self, request):
        self.message_user(request, 'Call-Put-Logs called')
        CallPutAction()
        self.message_user(request, 'Call-Put-Logs Done')
        return HttpResponseRedirectToReferrer(request)
    
    @button(change_form=True,
            html_attrs={'style': 'background-color:#FF3364;color:black'})
    def SATARU_GOJO(self, request):
        self.message_user(request, 'SATARU GOJO called')
        Minute1()
        self.message_user(request, 'SATARU GOJO Done')
        return HttpResponseRedirectToReferrer(request)

    @button(change_form=True,
            html_attrs={'style': 'background-color:#FFFD29;color:black'})
    def Notify_User(self, request):
        self.message_user(request, 'Notify Users Called')
        NotifyUsers()
        self.message_user(request, 'Notify Users Done')
        return HttpResponseRedirectToReferrer(request)