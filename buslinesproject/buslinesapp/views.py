from statistics import mean

from django.shortcuts import _get_queryset
from rest_framework import viewsets, generics, parsers, permissions, status
from .models import BusInfor, Account, Ticket, BusRoute, BusLine, Seat, Bill, Delivery
from . import serializers, pagination
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from .permission import IsBusOwnerRole, IsAdminRole, IsCustomerRole, IsEmployeeRole


# [get] lấy thông tin nhà xe /businfors/
class BusInforViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveAPIView):
    queryset = BusInfor.objects.filter(active=True)
    serializer_class = serializers.BusInforSerializer
    pagination_class = pagination.BusInforPaginator

    def perform_create(self, serializer):
        # Gán thuộc tính account bằng ID của user đang tạo
        serializer.save(account=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = serializers.BusInforDetailsSerializer(instance)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            self.permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            self.permission_classes = [IsBusOwnerRole]
        elif self.action == 'add_delivery':
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    def get_queryset(self):
        queryset = self.queryset
        is_delivery = self.request.query_params.get('is_delivery')
        name = self.request.query_params.get('name')
        if is_delivery:
            queryset = queryset.filter(is_delivery=is_delivery)
        if name:
            queryset = queryset.filter(name__contains=name)
        return queryset

    @staticmethod
    def generate_random_code(l):
        import secrets
        import string
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(l))

    @action(methods=['get', 'patch'], url_path='current-businfor', detail=False)
    def get_current_user(self, request):
        user = request.user
        try:
            businfor = BusInfor.objects.get(account=user.id)
        except BusInfor.DoesNotExist:
            return Response({"detail": "BusInfor not found for this user."}, status=status.HTTP_404_NOT_FOUND)
        if request.method.__eq__('PATCH'):
            for k, v in request.data.items():
                if k in ["active", "is_delivery_enabled", "bias"]:
                    return Response({"detail": "You don't have permission to patch this attribute"},
                                    status=status.HTTP_403_FORBIDDEN)
                else:
                    setattr(businfor, k, v)
            businfor.save()

        return Response(serializers.BusInforSerializer(businfor).data)

    @action(methods=['post'], url_path='busroutes', detail=True)
    def add_busroutes(self, request, pk):
        user = request.user
        businfor_instance = BusInfor.objects.get(pk=pk)
        if user.id == businfor_instance.account.id:
            c = businfor_instance.busroute_set.create(businfor=businfor_instance.id,
                                                      code=f"{request.data.get('code')}_{businfor_instance.code}",
                                                      active=True, starting_point=request.data.get('starting_point'),
                                                      destination=request.data.get('destination'),
                                                      active_time=request.data.get('active_time'),
                                                      distance=request.data.get('distance'),
                                                      estimated_duration=request.data.get('estimated_duration'),
                                                      frequency=request.data.get('frequency'),
                                                      fare=request.data.get('fare'))
            return Response(serializers.BusRouteSerializer(c).data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "You don't have permission to post busroute"},
                            status=status.HTTP_403_FORBIDDEN)

    @action(methods=['post'], url_path='delivery', detail=True)
    def add_delivery(self, request, pk):
        businfor_instance = self.get_object()
        print(businfor_instance.id)
        delivery = businfor_instance.delivery_set.create(businfor=businfor_instance.id,
                                                         code=f'{businfor_instance.code}_{self.generate_random_code(5)}',
                                                         sender_name=request.data.get('sender_name'),
                                                         sender_phone=request.data.get('sender_phone'),
                                                         sender_email=request.data.get('sender_email'),
                                                         receiver_name=request.data.get('receiver_name'),
                                                         receiver_phone=request.data.get('receiver_phone'),
                                                         receiver_email=request.data.get('receiver_email'),
                                                         weight=request.data.get('weight'),
                                                         content=request.data.get('content'))
        bill = Bill.objects.create(
            code=self.generate_random_code(7),
            payment_content=f"Payment for {delivery.weight} kg delivery",
            total=delivery.weight * 10000
        )
        delivery.bill = bill
        delivery.save()
        return Response(serializers.DeliverySerializer(delivery).data, status.HTTP_201_CREATED)


class BusInforDetailsViewSet(viewsets.ViewSet, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = BusInfor.objects.all()
    serializer_class = serializers.BusInforDetailsSerializer
    permission_classes = [IsAdminRole]


class BusRouteViewSet(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView):
    queryset = BusRoute.objects.all()
    serializer_class = serializers.BusRouteSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [permissions.AllowAny]
        elif self.action in ['partial_update', 'destroy']:
            self.permission_classes = [IsBusOwnerRole]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if user.id == instance.businfor.account.id:
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        else:
            return Response({"detail": "You don't have permission to patch orther busroute"}, status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        queryset = self.queryset
        starting_point = self.request.query_params.get('starting_point')
        destination = self.request.query_params.get('destination')
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(businfor__name__contains=name)
        if starting_point and destination:
            queryset = queryset.filter(starting_point__contains=starting_point)
            queryset = queryset.filter(destination__contains=destination)
        return queryset

    @action(methods=['get'], url_path='buslines', detail=True)
    def get_buslines(self, request, pk):
        busline = self.get_object().busline_set.filter(active=True)
        return Response(serializers.BusLineSerializer(busline, many=True).data, status.HTTP_200_OK)

    @action(methods=['post'], url_path='buslines', detail=True)
    def create_buslines(self, request, pk):
        user = request.user
        busroute_instance = self.get_object()
        if user.id == busroute_instance.businfor.account.id:
            busline = busroute_instance.busline_set.create(busroute=busroute_instance,
                                                           code=f"{busroute_instance.code}_{request.data.get('code')}",
                                                           active=request.data.get('active'),
                                                           departure_date_time=request.data.get('departure_date_time'),
                                                           arrival_excepted=request.data.get('arrival_excepted')
                                                           )
            return Response(serializers.BusLineSerializer(busline).data, status.HTTP_201_CREATED)
        else:
            return Response({"detail": "You don't have permission to post busline for orther busroute"},
                            status.HTTP_403_FORBIDDEN)


class BusLineDetailsViewSets(viewsets.ViewSet, generics.RetrieveUpdateAPIView):
    queryset = BusLine.objects.all()
    serializer_class = serializers.BusLineSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [permissions.AllowAny]
        elif self.action in ['partial_update', 'destroy']:
            self.permission_classes = [IsBusOwnerRole]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if user.id == instance.busroute.businfor.account.id:
            partial = kwargs.pop('partial', False)
            data = request.data
            allow_fields = ['arrival_actual']
            for k in data:
                if k not in allow_fields:
                    return Response({"detail": "You don't have permission to patch orther attribute"})
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        # else:
        #     return Response({"detail": "You don't have permission to patch orther busline"},
        #                     status.HTTP_403_FORBIDDEN)

        else:
            return Response({"detail": "You don't have permission to patch orther busline"}, status.HTTP_403_FORBIDDEN)

    @action(methods=['post'], url_path='seats', detail=True)
    def add_seats(self, request, pk):
        busline_instance = self.get_object()
        c = busline_instance.seat_set.create(busline=busline_instance,
                                             code=str(busline_instance.code) + "_" + request.data.get('code'),
                                             active=True,
                                             status='available')
        return Response(serializers.SeatSerializer(c).data, status=status.HTTP_201_CREATED)


class SeatViewSets(viewsets.ViewSet, generics.UpdateAPIView, generics.DestroyAPIView, generics.RetrieveAPIView,
                   generics.ListAPIView):
    queryset = Seat.objects.all()
    serializer_class = serializers.SeatSerializer
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def generate_random_code(l):
        import secrets
        import string
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(l))

    @action(methods=['post'], url_path='tickets', detail=True)
    def add_bill_and_ticket(self, request, pk):
        seat_instance = self.get_object()

        # Lấy thông tin người dùng
        customer = request.user
        seat_ids = request.data.get('seat_ids', [])

        # Kiểm tra và lấy thông tin các ghế
        seats = Seat.objects.filter(id__in=seat_ids, busline=seat_instance.busline)

        # Tính tổng tiền vé
        busroute = seat_instance.busline.busroute
        total_fare = busroute.fare * len(seats)

        # Tạo hóa đơn mới
        bill = Bill.objects.create(
            code=self.generate_random_code(7),
            payment_content=f"Payment for {len(seats)} tickets",
            total=total_fare
        )

        # Tạo vé và gán vào hóa đơn
        tickets = []
        for seat in seats:
            ticket = Ticket.objects.create(
                customer=customer,
                seat=seat,
                bill=bill,
                code=self.generate_random_code(10)
            )
            tickets.append(ticket)

        # Trả về dữ liệu vé
        ticket_serializer = serializers.TicketSerializer(tickets, many=True)
        return Response(ticket_serializer.data, status=status.HTTP_201_CREATED)


class AccountViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Account.objects.filter(is_active=True)
    serializer_class = serializers.AccountSerializer
    parser_classes = [parsers.MultiPartParser, ]

    def get_permissions(self):
        if self.action in ['get_current_account']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get', 'patch'], url_path='current-account', detail=False)
    def get_current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):
            for k, v in request.data.items():
                setattr(user, k, v)
            user.save()

        return Response(serializers.AccountSerializer(user).data)


class TicketViewSet(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = serializers.TicketSerializer

    def get_queryset(self):
        queryset = self.queryset
        code = self.request.query_params.get('code')
        phone = self.request.query_params.get('phone')
        bill = self.request.query_params.get('bill')
        if self.action == 'list':
            if code and phone:
                queryset = queryset.filter(code=code)
                queryset = queryset.filter(customer__phone=phone)
            elif bill:
                queryset = queryset.filter(bill__code=bill)
            else:
                queryset = []

        return queryset


class BillViewSet(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView):
    queryset = Bill.objects.all()
    serializer_class = serializers.BillSerializer

    def get_queryset(self):
        queryset = self.queryset
        code = self.request.query_params.get('code')
        if self.action == 'list':
            if code:
                queryset = queryset.filter(code=code)
            else:
                queryset = []

        return queryset


class DeliveryViewSet(viewsets.ViewSet, generics.UpdateAPIView, generics.ListAPIView):
    queryset = Delivery.objects.all()
    serializer_class = serializers.DeliverySerializer

    def get_queryset(self):
        queryset = self.queryset
        code = self.request.query_params.get('code')
        sender_phone = self.request.query_params.get('sender_phone')
        if self.action == 'list':
            if code and sender_phone:
                queryset = queryset.filter(code=code)
                queryset = queryset.filter(sender_phone=sender_phone)
            else:
                queryset = []

        return queryset
