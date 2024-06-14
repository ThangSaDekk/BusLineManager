from rest_framework import pagination


class BusInforPaginator(pagination.PageNumberPagination):
    page_size = 5


class BusRoutePaginator(pagination.PageNumberPagination):
    page_size = 3


class BusLinePaginator(pagination.PageNumberPagination):
    page_size = 3


class ReviewPaginator(pagination.PageNumberPagination):
    page_size = 5


class DeliveryPaginator(pagination.PageNumberPagination):
    page_size = 5


class BusRoutePaginator(pagination.PageNumberPagination):
    page_size = 5
