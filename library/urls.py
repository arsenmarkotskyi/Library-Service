from django.urls import path, include
from rest_framework import routers

from library.views import BookViewSet, BorrowingViewSet, PaymentViewSet

app_name = "library"

router = routers.DefaultRouter()
router.register("books", BookViewSet, basename="books")
router.register("borrowing", BorrowingViewSet, basename="borrowing")
router.register("payment", PaymentViewSet, basename="payment")

urlpatterns = [path("", include(router.urls))]
