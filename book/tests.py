from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from book.models import Book
from book.serializers import BookSerializer

BOOK_URL = reverse("book-list")


def sample_book(**params):
    defaults = {
        "cover": "HC",
        "title": "Sample book",
        "author": "Sample Author",
        "inventory": 5,
        "daily_fee": 2.99,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class UnauthenticatedBookTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_books(self):
        sample_book()
        sample_book()

        res = self.client.get(BOOK_URL)

        books = Book.objects.order_by("id")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results"), serializer.data)
