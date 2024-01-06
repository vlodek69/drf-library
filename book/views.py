from rest_framework.viewsets import ModelViewSet

from book.models import Book
from book.serializers import BookSerializer


class BookViewSet(ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
