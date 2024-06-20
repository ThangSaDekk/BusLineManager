from rest_framework import pagination


class BusInforPaginator(pagination.PageNumberPagination):
    page_size = 20


class BusRoutePaginator(pagination.PageNumberPagination):
    pass


class BusLinePaginator(pagination.PageNumberPagination):
    page_size = 20


class ReviewPaginator(pagination.PageNumberPagination):
    page_size = 5


class DeliveryPaginator(pagination.PageNumberPagination):
    page_size = 20


class BusRoutePaginator(pagination.PageNumberPagination):
    page_size = 5
