from django.contrib import admin
from .models import Account, BusRoute, BusLine, BusInfor, Seat, Delivery, Ticket, Review, Bill
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.urls import path
from django.db.models import Count, Sum
from django.template.response import TemplateResponse


# Register your models here.
class MyBusLineManagerAdminSite(admin.AdminSite):
    site_header = 'BusLineManagerOnline'

    def get_urls(self):
        return [path('businfors-stats/', self.stats_view)] + super().get_urls()

    def stats_view(self, request):
        busroute_stats = BusInfor.objects.annotate(c=Count('busroute__id')).values('id', 'name', 'c').filter(
            active=True)
        busline_stats = BusInfor.objects.annotate(c=Count('busroute__busline__id')).values('id', 'name', 'c').filter(
            active=True)
        bill_stats = BusInfor.objects.annotate(
            c=Sum('busroute__busline__seat__ticket__bill__total', distinct=True ,default=0)).values('id',
                                                                                         'name',
                                                                                         'c').filter(
            active=True)
        context = {
            "busroute_stats": busroute_stats,
            "busline_stats": busline_stats,
            "bill_stats": bill_stats,
        }
        return TemplateResponse(request, 'admin/stats.html', context=context)


admin_site = MyBusLineManagerAdminSite(name='BusLineManager')


class DeliveryForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Delivery
        fields = '__all__'


class MyAccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'date_joined', 'last_login', 'is_active', 'role']
    search_fields = ['username']


class MyDeliveryAdmin(admin.ModelAdmin):
    search_fields = ['id']
    form = DeliveryForm


class MyBusInforAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'phone', 'email', 'is_delivery_enabled']


class MyBusRouteAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'fare']


class MyBusLineAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'busroute', 'departure_date_time']


class MySeatAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'busline']


class MyBillAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'total', 'active']


class MyTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'customer', 'active']


class MyReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'rating', 'review_time', 'comment']


admin_site.register(Account, MyAccountAdmin)
admin_site.register(BusInfor, MyBusInforAdmin)
admin_site.register(BusRoute, MyBusRouteAdmin)
admin_site.register(BusLine, MyBusLineAdmin)
admin_site.register(Seat, MySeatAdmin)
admin_site.register(Bill, MyBillAdmin)
admin_site.register(Ticket, MyTicketAdmin)
admin_site.register(Delivery)
admin_site.register(Review, MyReviewAdmin)
