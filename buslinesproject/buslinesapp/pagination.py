from rest_framework import pagination


class BusInforPaginator(pagination.PageNumberPagination):
    pass


class BusRoutePaginator(pagination.PageNumberPagination):
    pass


class BusLinePaginator(pagination.PageNumberPagination):
    pass


class ReviewPaginator(pagination.PageNumberPagination):
    page_size = 5


class DeliveryPaginator(pagination.PageNumberPagination):
    pass


class BusRoutePaginator(pagination.PageNumberPagination):
    page_size = 5
