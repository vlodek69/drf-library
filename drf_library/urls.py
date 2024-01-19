"""
URL configuration for drf_library project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from book.urls import router as book_router
from borrowing.urls import router as borrowing_router


router = routers.DefaultRouter()
router.registry.extend(book_router.registry)
router.registry.extend(borrowing_router.registry)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("user.urls", namespace="user")),
    path("api/", include(router.urls)),
]
