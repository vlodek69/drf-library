from django.contrib.auth import get_user_model
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


def detail_url(book_id):
    return reverse("book-detail", args=[book_id])


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

    def test_retrieve_book_detail(self):
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_forbiden(self):
        payload = {
            "cover": "SC",
            "title": "Test book",
            "author": "Test Author",
            "inventory": 4,
            "daily_fee": 4.20,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookTests(UnauthenticatedBookTests):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_create_forbiden(self):
        payload = {
            "cover": "SC",
            "title": "Test book",
            "author": "Test Author",
            "inventory": 4,
            "daily_fee": 4.20,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
