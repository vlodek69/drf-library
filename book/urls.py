from rest_framework import routers

from book.views import BookViewSet


router = routers.DefaultRouter()
router.register("books", BookViewSet, basename="book")

app_name = "book"
