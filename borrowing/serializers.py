from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "user",
            "book",
            "borrowing_date",
            "expected_return_date",
            "actual_return_date",
        )

    def validate(self, data):
        if data["expected_return_date"] <= data["borrowing_date"]:
            raise serializers.ValidationError(
                "expected_return_date should be at least a day after borrowing_date."
            )
        if (
            data["actual_return_date"]
            and data["actual_return_date"] < data["borrowing_date"]
        ):
            raise serializers.ValidationError(
                "actual_return_date cannot be before borrowing_date."
            )

        return data


class BorrowingListSerializer(BorrowingSerializer):
    user = serializers.StringRelatedField(read_only=True, many=False)
    book = serializers.StringRelatedField(read_only=True, many=False)


class BorrowingDetailSerializer(BorrowingListSerializer):
    book = BookSerializer(read_only=True, many=False)
