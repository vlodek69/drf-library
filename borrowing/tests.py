import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)


BORROWING_URL = reverse("borrowing-list")
BORROWING_PAYLOAD = {
    "expected_return_date": (
            datetime.date.today() + datetime.timedelta(weeks=1)
    ),
}


def sample_borrowing(**params):
    defaults = BORROWING_PAYLOAD
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


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


def detail_url(borrowing_id):
    return reverse("borrowing-detail", args=[borrowing_id])


class UnauthenticatedBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.post(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)
        self.book = sample_book()

    def test_list_borrowings(self):
        user2 = get_user_model().objects.create_user(
            "test2@test.com", "testpass"
        )

        sample_borrowing(user=self.user, book=self.book)
        sample_borrowing(user=user2, book=self.book)
        sample_borrowing(user=self.user, book=self.book)

        res = self.client.get(BORROWING_URL)

        # assert user sees only theirs borrowings
        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results"), serializer.data)

    def test_retrieve_borrowing_detail(self):
        borrowing = sample_borrowing(user=self.user, book=self.book)

        url = detail_url(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(borrowing)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        BORROWING_PAYLOAD["book"] = self.book.id
        res = self.client.post(BORROWING_URL, BORROWING_PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        borrowing = Borrowing.objects.get(id=res.data["id"])
        BORROWING_PAYLOAD["book"] = self.book
        for key in BORROWING_PAYLOAD.keys():
            self.assertEqual(BORROWING_PAYLOAD[key], getattr(borrowing, key))

        # assert book inventory reduced by 1
        book_updated = Book.objects.get(id=BORROWING_PAYLOAD["book"].id)
        self.assertEqual(book_updated.inventory, self.book.inventory - 1)

    def test_cannot_create_when_book_inventory_zero(self):
        book = sample_book(inventory=0)
        BORROWING_PAYLOAD["book"] = book.id
        res = self.client.post(BORROWING_URL, BORROWING_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_borrowing(self):
        BORROWING_PAYLOAD["book"] = self.book.id
        create_res = self.client.post(BORROWING_URL, BORROWING_PAYLOAD)
        url = reverse("borrowing-return-book", args=[create_res.data["id"]])
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        borrowing = Borrowing.objects.get(id=create_res.data["id"])
        self.assertEqual(borrowing.actual_return_date, datetime.date.today())

        self.assertEqual(borrowing.book.inventory, self.book.inventory)


class AdminBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.book = Book.objects.create(
            cover="HC",
            title="Test book",
            author="Test Author",
            inventory=5,
            daily_fee=Decimal("4.20"),
        )

    def test_list_borrowings(self):
        user2 = get_user_model().objects.create_user(
            "test2@test.com", "testpass"
        )

        sample_borrowing(user=self.user, book=self.book)
        sample_borrowing(user=user2, book=self.book)
        sample_borrowing(user=self.user, book=self.book)

        res = self.client.get(BORROWING_URL)

        # assert admin user sees everyone's borrowings
        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get("results"), serializer.data)

    def test_patch_not_allowed(self):
        borrowing = sample_borrowing(user=self.user, book=self.book)
        payload = {
            "expected_return_date": (
                    datetime.date.today() + datetime.timedelta(weeks=2)
            ),
            "actual_return_date": datetime.date.today()
        }

        url = detail_url(borrowing.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_not_allowed(self):
        borrowing = sample_borrowing(user=self.user, book=self.book)
        url = detail_url(borrowing.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_filter_by_user_id(self):
        user2 = get_user_model().objects.create_user(
            "test2@test.com", "testpass"
        )

        sample_borrowing(user=self.user, book=self.book)
        sample_borrowing(user=user2, book=self.book)
        sample_borrowing(user=self.user, book=self.book)

        res = self.client.get(BORROWING_URL, {"user_id": user2.id})

        borrowings = Borrowing.objects.filter(user_id=user2.id)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.data.get("results"), serializer.data)

    def test_filter_borrowing_by_active(self):
        user2 = get_user_model().objects.create_user(
            "test2@test.com", "testpass"
        )

        borrowing = sample_borrowing(user=self.user, book=self.book)
        sample_borrowing(user=user2, book=self.book)
        sample_borrowing(user=self.user, book=self.book)

        # return one of the borrowings
        return_url = reverse("borrowing-return-book", args=[borrowing.id])
        self.client.post(return_url)

        res = self.client.get(BORROWING_URL, {"is_active": "true"})

        borrowings = Borrowing.objects.filter(actual_return_date=None)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.data.get("results"), serializer.data)
