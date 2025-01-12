import stripe
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import date
from django.conf import settings

from library.permissions import IsAdminOrIfAuthenticatedReadOnly
from library_service.tasks import handle_successful_payment


from library.models import Book, Borrowing, Payment
from library.serializers import (
    BookSerializer,
    BorrowingSerializer,
    PaymentSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)
from library_service.telegram_service import notify_new_borrowing


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        book = serializer.validated_data.get("book")
        if book.inventory <= 0:
            raise ValidationError({"error": "Книга не доступна для позичання."})
        book.save()
        borrowing = serializer.save(user=self.request.user)

        # Сповіщення через Telegram
        borrowing_details = f"Книга: '{borrowing.book.title}', Позичальник: {borrowing.user.email}, Очікувана дата повернення: {borrowing.expected_return_date}"
        notify_new_borrowing(borrowing_details)

    def get_queryset(self):
        user = self.request.user
        is_active = self.request.query_params.get("is_active")

        queryset = (
            Borrowing.objects.filter(user=user)
            if not user.is_staff
            else Borrowing.objects.all()
        )

        if is_active is not None:
            is_active = is_active.lower() == "true"
            queryset = queryset.filter(actual_return_date__isnull=is_active)
        return queryset

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        if borrowing.actual_return_date:
            return Response(
                {"detail": "This book has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        borrowing.actual_return_date = date.today()
        borrowing.save()

        borrowing.book.inventory += 1
        borrowing.book.save()

        return Response(
            {"detail": "Book return processed successfully."}, status=status.HTTP_200_OK
        )


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing, borrowing_id):
    borrowing = get_object_or_404(Borrowing, pk=borrowing_id)
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        client_reference_id=str(borrowing.id),
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": borrowing.book.title,
                    },
                    "unit_amount": int(borrowing.price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:8000/library/payments/success/?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://localhost:8000/library/payments/cancel/",
    )

    return JsonResponse(
        {
            "session_url": session.url,
            "session_id": session.id,
        }
    )


def payment_success(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        return JsonResponse({"error": "Session ID is missing."}, status=400)

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            borrowing_id = session.client_reference_id
            borrowing = get_object_or_404(Borrowing, pk=borrowing_id)

            payment_details = (
                f"Користувач: {borrowing.user.email}\n"
                f"Книга: {borrowing.book.title}\n"
                f"Сума: {borrowing.price} $"
            )

            handle_successful_payment.delay(payment_details)
            return JsonResponse({"message": "Payment was successful!"})
    except stripe.error.StripeError as e:
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"message": "Payment was successful!"})


def payment_cancel(request):
    return JsonResponse({"message": "Payment was cancelled."})


def payment_status(request, session_id):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return JsonResponse(
            {
                "session_id": session.id,
                "payment_status": session.payment_status,
                "status": session.status,
            }
        )
    except stripe.error.StripeError as e:
        return JsonResponse({"error": str(e)}, status=400)
