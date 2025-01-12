from django.urls import path, include
from rest_framework import routers

from library.views import (
    BookViewSet,
    BorrowingViewSet,
    PaymentViewSet,
    # create_payment,
    # payment_response,
    payment_success,
    payment_cancel,
    create_stripe_session,
    payment_status,
)

app_name = "library"

router = routers.DefaultRouter()
router.register("books", BookViewSet, basename="books")
router.register(r"borrowings", BorrowingViewSet, basename="borrowing")
router.register("payment", PaymentViewSet, basename="payment")


urlpatterns = [
    path("", include(router.urls)),
    path("payments/<int:borrowing_id>/", create_stripe_session, name="create_payment"),
    path("payments/success/", payment_success, name="payment_success"),
    path("payments/cancel/", payment_cancel, name="payment_cancel"),
    path("payments/status/<str:session_id>/", payment_status, name="payment_status"),
    # path("webhook/stripe/", stripe_webhook, name="stripe-webhook"),
]
