from rest_framework import pagination


class BusInforPaginator(pagination.PageNumberPagination):
    page_size = 20


class BusRoutePaginator(pagination.PageNumberPagination):
    page_size = 20


class BusLinePaginator(pagination.PageNumberPagination):
    page_size = 20


class ReviewPaginator(pagination.PageNumberPagination):
    page_size = 6


class DeliveryPaginator(pagination.PageNumberPagination):
    page_size = 20


class BusRoutePaginator(pagination.PageNumberPagination):
    page_size = 5
