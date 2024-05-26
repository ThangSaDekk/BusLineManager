from rest_framework import pagination


class BusInforPaginator(pagination.PageNumberPagination):
    page_size = 2
