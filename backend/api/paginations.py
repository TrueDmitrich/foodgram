from rest_framework import pagination


class LimitPagePagination(pagination.PageNumberPagination):

    page_size_query_param = 'limit'
    page_size = 6
