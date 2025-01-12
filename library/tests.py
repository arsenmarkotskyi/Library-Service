from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from datetime import timedelta, date
import json
from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch
from library.models import Book, Borrowing
from library.views import create_stripe_session
from library_service.telegram_service import (
    notify_new_borrowing,
    notify_overdue_borrowing,
    notify_successful_payment,
)

BORROWING_URL = reverse("library:borrowing-list")
BOOK_URL = reverse("library:books-list")
User = get_user_model()


class UnauthenticatedLibraryApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_required_for_book_list(self):
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BookViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@gmail.com", password="1qazcde3"
        )
        self.book = Book.objects.create(
            title="Test Book", author="Author", inventory=10, daily_fee=2.50
        )

    def test_list_books_as_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {
            "title": "Test Book",
            "author": "Author",
            "inventory": 10,
            "daily_fee": 2.50,
        }
        response = self.client.post(BOOK_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class BorrowingViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.book = Book.objects.create(
            title="Test Book", author="Author", inventory=10, daily_fee=2.50
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=date.today() + timedelta(days=7),
        )

    def test_create_borrowing_successful(self):
        self.client.force_authenticate(user=self.user)
        data = {
            "book": self.book.id,
            "expected_return_date": date.today() + timedelta(days=7),
        }
        response = self.client.post(BORROWING_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_borrowings_filtered_by_active(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(BORROWING_URL, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_return_book(self):
        self.client.force_authenticate(user=self.user)
        initial_inventory = self.book.inventory
        response = self.client.post(
            reverse("library:borrowing-return-book", kwargs={"pk": self.borrowing.id})
        )
        self.borrowing.refresh_from_db()
        self.book.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.assertEqual(self.book.inventory, initial_inventory + 1)


class PaymentViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="payuser@example.com", password="password123"
        )
        self.book = Book.objects.create(
            title="Pay Book", author="Pay Author", inventory=5, daily_fee=3.00
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=date.today() + timedelta(days=7),
        )

    @patch("stripe.checkout.Session.create")
    def test_create_stripe_session(self, mock_create):
        mock_create.return_value = type(
            "Session", (object,), {"id": "sess_123", "url": "http://example.com"}
        )
        response = create_stripe_session(self.borrowing, self.borrowing.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        self.assertIn("session_url", response_data)

    @patch("stripe.checkout.Session.retrieve")
    @patch("library_service.tasks.handle_successful_payment.delay")
    def test_payment_success(self, mock_task, mock_retrieve):
        mock_retrieve.return_value = type(
            "Session",
            (object,),
            {"payment_status": "paid", "client_reference_id": str(self.borrowing.id)},
        )
        response = self.client.get(
            reverse("library:payment_success") + "?session_id=sess_123"
        )
        mock_task.assert_called_once()
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TelegramNotificationTest(TestCase):
    @patch("library_service.telegram_service.send_notification")
    def test_notify_new_borrowing(self, mock_send):
        notify_new_borrowing("Test borrowing details")
        mock_send.assert_called_once()

    @patch("library_service.telegram_service.send_notification")
    def test_notify_overdue_borrowing(self, mock_send):
        notify_overdue_borrowing("Test overdue details")
        mock_send.assert_called_once()

    @patch("library_service.telegram_service.send_notification")
    def test_notify_successful_payment(self, mock_send):
        notify_successful_payment("Payment details")
        mock_send.assert_called_once()
