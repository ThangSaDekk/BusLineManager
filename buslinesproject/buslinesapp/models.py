from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from ckeditor.fields import RichTextField


# model tài khoản
class Account(AbstractUser):
    # Các phân quyền đăng nhập
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('busowner', 'BusOwner'),
        ('employee', 'Employee'),
    ]
    # Thuộc tính
    # Vai trò
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Customer')
    # Số liên lạc
    phone = models.CharField(max_length=20, null=True, unique=True)
    # Địa chỉ
    address = models.CharField(max_length=255, null=True)
    # Ảnh đại diện
    avatar = CloudinaryField(null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class BaseModel(models.Model):
    code = models.CharField(max_length=255, default="Empty", unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.code

    class Meta:
        abstract = True


class BusInfor(BaseModel):
    # khóa ngoại quan hệ 1 - 1 với tài khoản chủ xe
    account = models.ForeignKey(Account, on_delete=models.CASCADE, unique=True)
    # Thuộc tính
    name = models.CharField(max_length=255, null=False)  # tên công ty
    phone = models.CharField(max_length=20, null=False)  # số điện thoại
    email = models.EmailField()  # email công ty
    is_delivery_enabled = models.BooleanField(default=False)  # có giao hàng không ?
    bias = models.FloatField(default=10)  # điểm để đánh giá so sánh


# Tuyến xe
class BusRoute(BaseModel):
    # khóa ngoại quan hệ 1 - n với thông tin nhà xe
    businfor = models.ForeignKey(BusInfor, on_delete=models.CASCADE)
    # Thuộc tính
    starting_point = models.CharField(max_length=255, null=False)  # điểm xuất phát
    destination = models.CharField(max_length=255, null=False)  # điểm kết thúc
    active_time = models.CharField(max_length=255, null=False)  # thời gian hoạt động trong ngày
    distance = models.IntegerField(null=False)  # khoảng cách đơn vị là km
    estimated_duration = models.CharField(null=False, max_length=100)  # thời gian ước tính hoàn thành
    frequency = models.CharField(max_length=100, null=False)  # tần suất
    fare = models.FloatField(null=False)  # giá vé
    bias = models.FloatField(default=10)  # điểm để đánh giá so sánh


# Chuyến Xe
class BusLine(BaseModel):
    # khóa ngoại quan hệ 1 nhiều với tuyến xe
    busroute = models.ForeignKey(BusRoute, on_delete=models.CASCADE)
    # Thuộc tính
    departure_date_time = models.DateTimeField()  # ngày giờ khởi hành
    arrival_excepted = models.DateTimeField()  # ngày và giờ đến dự kiến
    arrival_actual = models.DateTimeField(null=True, blank=True)  # ngày và giờ đến thực tế


# Ghế
class Seat(BaseModel):
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('available', 'Available'),
        ('cancelled', 'Cancelled'),
    ]
    # khóa ngoại quan hệ 1 - n  với chuyến xe
    busline = models.ForeignKey(BusLine, on_delete=models.CASCADE)
    # Thuộc tính
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Available')

    class Meta:
        unique_together = ('busline', 'code')


class Bill(BaseModel):
    PAYMENT_METHOD = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    # Thuộc tính
    payment_time = models.DateTimeField(null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD, default='Offline')
    payment_code = models.CharField(max_length=255, null=True)
    payment_content = models.CharField(max_length=255, null=False)
    total = models.FloatField(null=False)


# Vé
class Ticket(BaseModel):
    # khóa ngoại quan hệ 1 - 1 với khách hàng
    customer = models.ForeignKey(Account, on_delete=models.CASCADE)
    # khóa ngoại quan hệ 1 - 1 với vé xe
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, unique=True)
    # khóa ngoại quan hệ 1 - n với hóa đơn
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, null=True)
    # Thuộc tính
    booking_time = models.DateTimeField(auto_now_add=True)


# Giao hàng
class Delivery(BaseModel):
    # khóa ngoại chuyến xe
    businfor = models.ForeignKey(BusInfor, on_delete=models.CASCADE)
    # khóa ngoại quan hệ 1 - 1 với hóa đơn
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, unique=True, null= True)
    # Thuôc tính
    sender_name = models.CharField(max_length=255)  # tên người gửi
    sender_phone = models.CharField(max_length=15)  # số điện thoại người gửi
    sender_email = models.CharField(max_length=255, null=True)  # email người gửi
    receiver_name = models.CharField(max_length=255)  # tên người nhận
    receiver_phone = models.CharField(max_length=15)  # số điện thoại người nhân
    receiver_email = models.CharField(max_length=255, null=True)  # email người nhận
    delivery_time = models.DateTimeField(auto_now_add=True)  # Thời gian người gửi gửi
    receive_time = models.DateTimeField(null=True)  # Thời gian người nhận nhận hàng
    delivery_status = models.BooleanField(default=False)  # False là chưa giao, True là giao rồi
    weight = models.FloatField(default=0)  # Trọng lượng
    content = RichTextField(null=True)

# Đánh giá
# class Review(BaseModel):
#     # khóa ngoại tới khách hàng
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
#
#     class Star(models.IntegerChoices):
#         BAD = 1
#         NOT_GOOD = 2
#         MANUAL = 3
#         GOOD = 4
#         EXCELLENT = 5
#
#     rating = models.IntegerField(choices=Star)
#     comment = models.CharField(max_length=255)
#     review_time = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         abstract = True
#
#
# # Đánh giá chuyến xe
# class RevieBusTimeLine(Review):
#     # khóa ngoại tới Chuyến xe
#     bustimeline = models.ForeignKey(BusTimeLine, on_delete=models.CASCADE)

#
# # Đánh giá giao hàng
# class ReviewDelivery(Review):
#     # Khóa ngoại tới Giao hàng
#     delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)
