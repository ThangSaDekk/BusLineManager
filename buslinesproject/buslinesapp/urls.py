from django.urls import path, include
from rest_framework import routers
from . import views

r = routers.DefaultRouter()
r.register('businfors', views.BusInforViewSet, 'businfors')
r.register('businfor', views.BusInforDetailsViewSet, 'businfor')
r.register('accounts', views.AccountViewSet, 'accounts')
r.register('busroutes', views.BusRouteViewSet, 'busroutes')
r.register('tickets', views.TicketViewSet, 'tickets')
r.register('busline', views.BusLineDetailsViewSets, 'busline')
r.register('seat', views.SeatViewSets, 'seat')
r.register('bills', views.BillViewSet, 'bills')
r.register('deliverys', views.DeliveryViewSet,'deliverys')


urlpatterns = [
    path('', include(r.urls)),

]
