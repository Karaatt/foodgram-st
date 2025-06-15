from rest_framework.pagination import PageNumberPagination


class CustomPagePagination(PageNumberPagination):
    page_size_query_param = "limit"
