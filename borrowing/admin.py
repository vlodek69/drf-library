from django.contrib import admin

from borrowing.models import Borrowing

@admin.register(Borrowing)
class BookAdmin(admin.ModelAdmin):
    list_display = ("borrowing_date", "expected_return_date", "actual_return_date", "book", "user")
    search_fields = ("book", "user")
