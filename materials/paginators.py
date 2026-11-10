from rest_framework.pagination import PageNumberPagination


class MaterialsPaginator(PageNumberPagination):
    page_size = 5                  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр запроса для изменения размера страницы пользователем
    max_page_size = 10             # Максимальное ограничение количества элементов на странице