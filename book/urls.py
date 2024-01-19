from rest_framework import routers

from book.views import BookViewSet


router = routers.DefaultRouter()
router.register("books", BookViewSet)

app_name = "book"
