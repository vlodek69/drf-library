from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

from book.models import Book
from book.permissions import IsAdminOrReadOnly
from book.serializers import BookSerializer


class BookPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = BookPagination
