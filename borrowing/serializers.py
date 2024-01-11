import datetime

from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrowing_date",
            "expected_return_date",
        )

    def validate(self, data):
        borrowing_date = data.get("borrowing_date", datetime.date.today())

        if data.get("expected_return_date") <= borrowing_date:
            raise serializers.ValidationError(
                "expected_return_date should be at least a day after "
                "borrowing_date."
            )
        if (
            data.get("actual_return_date")
            and data.get("actual_return_date") < borrowing_date
        ):
            raise serializers.ValidationError(
                "actual_return_date cannot be before borrowing_date."
            )

        return data

    def validate_book(self, book):
        if not book.inventory:
            raise serializers.ValidationError("Out of stock!")
        return book

    def create(self, validated_data):
        book = validated_data.get("book")
        book.inventory -= 1
        book.save()

        return Borrowing.objects.create(**validated_data)


class BorrowingListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True, many=False)
    book = serializers.StringRelatedField(read_only=True, many=False)


class BorrowingDetailSerializer(BorrowingListSerializer):
    book = BookSerializer(read_only=True, many=False)
