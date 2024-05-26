from django.contrib import admin
from .models import Account, BusRoute, BusLine, BusInfor, Seat, Delivery, Ticket, Bill
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms


# Register your models here.


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


admin.site.register(Account, MyAccountAdmin)
admin.site.register(BusInfor, MyBusInforAdmin)
admin.site.register(BusRoute, MyBusRouteAdmin)
admin.site.register(BusLine, MyBusLineAdmin)
admin.site.register(Seat, MySeatAdmin)
admin.site.register(Bill, MyBillAdmin)
admin.site.register(Ticket, MyTicketAdmin )
admin.site.register(Delivery)
