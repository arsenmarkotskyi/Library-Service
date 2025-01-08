from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from datetime import date
from library_service.tasks import create_new_borrowing


from library.models import Book, Borrowing, Payment
from library.serializers import (
    BookSerializer,
    BorrowingSerializer,
    PaymentSerializer,
)
from library_service.telegram_service import notify_new_borrowing


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    # def get_serializer_class(self):
    #     if self.action == "list":
    #         return BookListSerializer
    #     return BookSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def perform_create(self, serializer):
        # serializer.save(user=self.request.user)
        book = serializer.validated_data.get("book")
        if book.inventory <= 0:
            raise ValidationError({"error": "Книга не доступна для позичання."})
        book.inventory -= 1
        book.save()
        borrowing = serializer.save(user=self.request.user)

        # Сповіщення через Telegram
        borrowing_details = f"Книга: '{borrowing.book.title}', Позичальник: {borrowing.user.username}, Очікувана дата повернення: {borrowing.expected_return_date}"
        notify_new_borrowing(borrowing_details)

    def get_queryset(self):
        user = self.request.query_params.get("user")
        is_active = self.request.query_params.get("is_active")

        queryset = super().get_queryset()

        if user:
            queryset = queryset.filter(user=user)

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
