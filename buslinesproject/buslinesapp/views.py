from queue import Empty
from rest_framework import viewsets, generics, parsers, permissions, status
from .models import BusInfor, Account, Ticket, BusRoute, BusLine, Seat, Bill, Delivery, Review
from . import serializers, pagination
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from .permission import IsBusOwnerRole, IsAdminRole, IsCustomerRole, IsEmployeeRole, ReviewOwner
from django.core.mail import send_mail
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


# [get] lấy thông tin nhà xe /businfors/
class BusInforViewSet(viewsets.ViewSet, generics.ListCreateAPIView, generics.RetrieveAPIView):
    queryset = BusInfor.objects.all().order_by('-bias')
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
        if self.action == ['list', 'retrieve', 'add_delivery']:
            self.permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            self.permission_classes = [IsBusOwnerRole]
        elif self.action in ['get_and_add_review', 'get_add_delivery', 'get_add_busroute']:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        queryset = self.queryset
        is_delivery = self.request.query_params.get('is_delivery_enabled')
        name = self.request.query_params.get('name')
        active = self.request.query_params.get('active')
        if is_delivery:
            queryset = queryset.filter(is_delivery_enabled=is_delivery)
        if name:
            queryset = queryset.filter(name__contains=name)
        if active:
            queryset = queryset.filter(active=active)
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

        return Response(serializers.BusInforDetailsSerializer(businfor).data)

    @action(methods=['get', 'post'], url_path='busroutes', detail=True)
    def get_add_busroute(self, request, pk):
        if request.method == 'GET':
            if request.user.id == self.get_object().account.id or request.user.role == "admin":
                active_param = self.request.query_params.get('isActive', None)
                print(type(active_param))
                busroute = self.get_object().busroute_set.all().order_by('-id')

                if active_param is not None:
                    if active_param == '1':
                        print(1)
                        busroute = busroute.filter(active=True)
                    elif active_param == '0':
                        busroute = busroute.filter(active=False)
                paginator = pagination.BusRoutePaginator()
                page = paginator.paginate_queryset(busroute, request)

                if page is not None:
                    serializer = serializers.BusRouteSerializer(page, many=True)
                    return paginator.get_paginated_response(serializer.data)
                return Response(serializers.BusRouteSerializer(busroute, many=True), status.HTTP_200_OK)
            else:
                return Response({"detail": "You don't have permission to get busroute"},
                                status=status.HTTP_403_FORBIDDEN)

        if request.method == 'POST':
            user = request.user
            businfor_instance = self.get_object()
            if user.id == businfor_instance.account.id:
                c = businfor_instance.busroute_set.create(businfor=businfor_instance.id,
                                                          code=f"{request.data.get('code')}_{businfor_instance.code}",
                                                          active=True,
                                                          starting_point=request.data.get('starting_point'),
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
        else:
            return Response({"details": "Phương thức không được hỗ trợ"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['get', 'post'], url_path='deliverys', detail=True)
    def get_add_delivery(self, request, pk):
        if request.method == 'GET':
            if request.user.id == self.get_object().account.id:
                deliverys = self.get_object().delivery_set.filter(active=True).order_by('-id')
                paginator = pagination.DeliveryPaginator()
                page = paginator.paginate_queryset(deliverys, request)

                if page is not None:
                    serializer = serializers.DeliverySerializer(page, many=True)
                    return paginator.get_paginated_response(serializer.data)
                return Response(serializers.DeliverySerializer(deliverys, many=True), status.HTTP_200_OK)
            else:
                return Response({"detail": "You don't have permission to get delivery"},
                                status=status.HTTP_403_FORBIDDEN)

        if request.method == 'POST':
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
                total=int(delivery.weight) * 10000
            )
            delivery.bill = bill
            delivery.save()
            return Response(serializers.DeliverySerializer(delivery).data, status.HTTP_201_CREATED)
        else:
            return Response({"details": "Phương thức không được hỗ trợ"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['get', 'post'], url_path='reviews', detail=True)
    def get_and_add_review(self, request, pk):
        if request.method == 'GET':
            reviews = self.get_object().review_set.select_related('customer').order_by('-id')

            paginator = pagination.ReviewPaginator()
            page = paginator.paginate_queryset(reviews, request)

            if page is not None:
                serializer = serializers.ReviewSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
            return Response(serializers.ReviewSerializer(reviews, many=True), status.HTTP_200_OK)

        if request.method == 'POST':
            ticket_code = request.data.get('ticket_code')
            businfor_instance = self.get_object()
            ticket_instance = Ticket.objects.get(code=ticket_code)
            # sự khác biệt giữa get và filter
            # get lấy đối tượng duy nhất
            # filter ra tập hợp
            # lưu ý tránh lỗi
            if ticket_instance.seat.busline.busroute.businfor.id == businfor_instance.id and ticket_instance.customer.id == request.user.id:
                c = businfor_instance.review_set.create(comment=request.data.get('comment'),
                                                        rating=request.data.get('rating'),
                                                        customer=request.user,
                                                        businfor=businfor_instance,
                                                        ticket=ticket_instance,
                                                        code=ticket_code,
                                                        active=True
                                                        )
                return Response(serializers.ReviewSerializer(c).data, status.HTTP_201_CREATED)
            else:
                return Response({"details": "Some Error !!"}, status.HTTP_403_FORBIDDEN)
        return Response({"details": "Phương thức không được hỗ trợ"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class BusInforDetailsViewSet(viewsets.ViewSet, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = BusInfor.objects.all()
    serializer_class = serializers.BusInforDetailsSerializer


class BusRouteViewSet(viewsets.ViewSet, generics.ListAPIView, generics.UpdateAPIView):
    queryset = BusRoute.objects.all().order_by('-bias')
    serializer_class = serializers.BusRouteSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [permissions.AllowAny]
        elif self.action in ['partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        if user.id == instance.businfor.account.id or user.role == 'admin':
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        else:
            return Response({"detail": "You don't have permission to patch orther busroute"}, status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        queryset = self.queryset
        starting_point = self.request.query_params.get('starting_point')
        destination = self.request.query_params.get('destination')
        name = self.request.query_params.get('name')
        active = self.request.query_params.get('active')
        businfor = self.request.query_params.get('businfor_id')
        if name:
            queryset = queryset.filter(businfor__name__contains=name)
        if starting_point and destination:
            queryset = queryset.filter(starting_point__contains=starting_point)
            queryset = queryset.filter(destination__contains=destination)
        if active:
            queryset = queryset.filter(active=active)
        if businfor:
            queryset = queryset.filter(businfor=businfor)
        return queryset

    @action(methods=['get', 'post'], url_path='buslines', detail=True)
    def get_post_buslines(self, request, pk=None):
        busroute_instance = self.get_object()

        if request.method == 'GET':
            buslines = busroute_instance.busline_set.filter(active=True)

            paginator = pagination.BusLinePaginator()
            paginated_buslines = paginator.paginate_queryset(buslines, request)
            serialized_buslines = serializers.BusLineSerializer(paginated_buslines, many=True).data
            return paginator.get_paginated_response(serialized_buslines)

        elif request.method == 'POST':
            user = request.user
            if user.id == busroute_instance.businfor.account.id:
                busline = busroute_instance.busline_set.create(
                    busroute=busroute_instance,
                    code=f"{busroute_instance.code}_{request.data.get('code')}",
                    active=request.data.get('active'),
                    departure_date_time=request.data.get('departure_date_time'),
                    arrival_excepted=request.data.get('arrival_excepted')
                )
                serialized_busline = serializers.BusLineSerializer(busline).data
                return Response(serialized_busline, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": "You don't have permission to post busline for other busroute"},
                                status=status.HTTP_403_FORBIDDEN)


class BusLineDetailsViewSets(viewsets.ViewSet, generics.RetrieveUpdateAPIView):
    queryset = BusLine.objects.all()
    serializer_class = serializers.BusLineSerializer
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action == 'get_add_seats':
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
            allow_fields = ['arrival_actual', 'active']
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

    @action(methods=['get', 'post'], url_path='seats', detail=True)
    def get_add_seats(self, request, pk):
        busline_instance = self.get_object()
        if request.method == 'POST':
            c = busline_instance.seat_set.create(busline=busline_instance,
                                                 code=str(busline_instance.code) + "_" + request.data.get('code'),
                                                 active=True,
                                                 status='available')
            return Response(serializers.SeatSerializer(c).data, status=status.HTTP_201_CREATED)
        if request.method == 'GET':
            seats = busline_instance.seat_set.filter(active=True)
            serialized_seats = serializers.SeatSerializer(seats, many=True).data
            return Response(serialized_seats, status.HTTP_200_OK)


class SeatViewSets(viewsets.ViewSet, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Seat.objects.all()
    serializer_class = serializers.SeatSerializer

    def get_permissions(self):
        if self.action == 'add_bill_and_ticket':
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'list':
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

    @staticmethod
    def generate_random_code(l):
        import secrets
        import string
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(l))

    @action(methods=['post'], url_path='tickets', detail=False)
    def add_bill_and_ticket(self, request):
        seat_ids = request.data.get('chose_seats_ids', [])

        customer = request.user
        if seat_ids is not Empty:
            seat_instances = []
            for seat_id in seat_ids:
                seat = Seat.objects.get(id=seat_id)
                seat_instances.append(seat)
            busroute_instance = seat_instances[0].busline.busroute
            total_fare = busroute_instance.fare * len(seat_instances)

            # Tạo hóa đơn mới
            bill = Bill.objects.create(
                code=self.generate_random_code(7),
                payment_content=f"Payment for {len(seat_instances)} tickets",
                total=total_fare
            )

            # Tạo vé và gán vào hóa đơn
            tickets = []
            for seat in seat_instances:
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
        else:
            Response({"details: Empty Seat "}, status.HTTP_404_NOT_FOUND)


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
        user.last_login = datetime.now() + timedelta(hours=7)
        user.save()
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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        businfor_instance = BusInfor.objects.get(id=instance.businfor.id)
        key1 = 'delivery_status' in request.data
        key2 = 'receive_time' in request.data
        key3 = 'active' in request.data
        html_content = instance.content

        # Sử dụng BeautifulSoup để loại bỏ các thẻ HTML
        soup = BeautifulSoup(html_content, "html.parser")
        text_content = soup.get_text()

        if key1 and key2 and len(request.data) == 2:
            datetime_obj = datetime.fromisoformat(request.data.get('receive_time'))
            formatted_time = f"{datetime_obj:%d-%m-%Y %H:%M:%S}"

            message = (
                f"Đơn hàng của quý khách đã được gửi tới người nhận !! \n Cảm ơn quý khách đã sử dụng dịch vụ của nhà xe {businfor_instance.name}!! \n\tMã đơn hàng:{instance.code}\n\tNgười nhận: {instance.receiver_name}\n\tThời gian nhận: {formatted_time} "
                f"\n Quý khách có thắc mắc liên hệ {businfor_instance.phone} để nhận được trợ giúp")
            email = instance.sender_email
            # print(email)
            name = "Đơn hàng của bạn đã được nhận !!"
            send_mail(name, message, 'settings.EMAIL_HOST_USER', [email], fail_silently=False)

        if key3 and len(request.data) == 1:
            message = (
                f"Đơn hàng của quý khách đã được gửi tới !! \n Quý khách vui lòng đến nhà xe {businfor_instance.name} để nhận hàng !! \n\tMã đơn hàng:{instance.code}\n\tNgười gửi: {instance.sender_name}\n\tLời nhắn: {text_content} "
                f"\n Quý khách có thắc mắc liên hệ {businfor_instance.phone} để nhận được trợ giúp")
            email = instance.receiver_email
            # print(email)
            name = "Đơn hàng của bạn đã tới !!"
            send_mail(name, message, 'settings.EMAIL_HOST_USER', [email], fail_silently=False)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ReviewViewSet(viewsets.ViewSet, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [ReviewOwner]
