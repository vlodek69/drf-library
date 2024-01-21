from rest_framework import routers

from borrowing.views import BorrowingViewSet


router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet, basename="borrowing")

app_name = "borrowing"
