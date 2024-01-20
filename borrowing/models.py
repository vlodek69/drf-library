from django.conf import settings
from django.db import models
from django.db.models import Q, F

from book.models import Book


class Borrowing(models.Model):
    borrowing_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True, default=None)
    book = models.ForeignKey(
        to=Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )

    class Meta:
        ordering = ["-borrowing_date"]
        constraints = [
            models.CheckConstraint(
                check=Q(expected_return_date__gt=F("borrowing_date")),
                name="expected_return_date_cannot_be_before_borrowing",
            ),
            models.CheckConstraint(
                check=Q(actual_return_date__gte=F("borrowing_date")),
                name="actual_return_date_cannot_be_before_borrowing",
            ),
        ]

    def __str__(self):
        return str(self.borrowing_date) + " " + self.book.title

    def telegram_message(self) -> str:
        return (
            f"Borrowing ID: {self.id}"
            f"\nBorrowing date: {self.borrowing_date}"
            f"\nExpected return date: {self.expected_return_date}"
            f"\nBook: {self.book.__str__()}"
            f"\nLeft in inventory: {self.book.inventory}"
            f"\nUser email: {self.user.__str__()}"
            f"\nUser ID: {self.user.id}"
        )
