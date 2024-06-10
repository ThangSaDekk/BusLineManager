from rest_framework import serializers
from .models import BusInfor, Account, BusRoute, BusLine, Ticket, Seat, Bill, Delivery, Review


class BusInforSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = BusInfor
        fields = ['id', 'code', 'name', 'phone', 'email', 'avatar', 'address']
        read_only_fields = ['account']

    def get_avatar(self, obj):
        if obj.account.avatar:
            return obj.account.avatar.url
        return None

    def get_address(self, obj):
        if obj.account.address:
            return obj.account.address
        return None


class BusInforDetailsSerializer(BusInforSerializer):
    class Meta:
        model = BusInforSerializer.Meta.model
        fields = BusInforSerializer.Meta.fields + ['is_delivery_enabled', 'bias', 'created_date', 'updated_date',
                                                   'active']


class BusRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusRoute
        fields = '__all__'


class BusLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusLine
        fields = '__all__'


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = '__all__'


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'


class AccountSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['avatar'] = instance.avatar.url

        return rep

    def create(self, validated_data):  # băm password khi post
        data = validated_data.copy()
        user = Account(**data)
        user.set_password(user.password)
        user.save()

        return user

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = Account
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'password', 'role', 'phone', 'address',
                  'avatar']

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }


class TicketSerializer(serializers.ModelSerializer):
    seat = serializers.SerializerMethodField

    class Meta:
        model = Ticket
        fields = '__all__'


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'


class DeliverySerializer(serializers.ModelSerializer):
    read_only_fields = ['bill']

    class Meta:
        model = Delivery
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    account = AccountSerializer()

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'review_time', 'account']
