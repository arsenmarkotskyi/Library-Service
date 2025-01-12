from celery import shared_task
from .telegram_service import (
    notify_overdue_borrowing,
    notify_successful_payment,
)
from library.models import Borrowing
from datetime import date


@shared_task
def handle_successful_payment(payment_details):
    notify_successful_payment(payment_details)


@shared_task
def check_overdue_borrowings():

    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lt=date.today(),
        actual_return_date__isnull=True,
    )
    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            borrowing_details = (
                f"Книга: '{borrowing.book.title}', "
                f"Позичальник: {borrowing.user.email}, "
                f"Дата позики: {borrowing.borrow_date}, "
                f"Очікувана дата повернення: {borrowing.expected_return_date}"
            )
            notify_overdue_borrowing(borrowing_details)
    else:
        notify_overdue_borrowing("No borrowings overdue today!")
