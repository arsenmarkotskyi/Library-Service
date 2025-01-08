from django.urls import path, include
from rest_framework import routers

from library.views import (
    BookViewSet,
    BorrowingViewSet,
    PaymentViewSet,
    # borrow_book
)

app_name = "library"

router = routers.DefaultRouter()
router.register("books", BookViewSet, basename="books")
router.register(r"borrowing", BorrowingViewSet, basename="borrowing")
router.register("payment", PaymentViewSet, basename="payment")


urlpatterns = [
    path("", include(router.urls)),
    # path("borrow/", borrow_book, name="borrow_book"),
]
