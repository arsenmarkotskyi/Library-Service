from django.db import models
from django.conf import settings
from datetime import date


class Book(models.Model):
    class CoverType(models.TextChoices):
        HARD = "H", "Hard"
        SOFT = "S", "Soft"

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.CharField(
        choices=CoverType.choices, default=CoverType.HARD, max_length=1
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.title


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        "Book", on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    @property
    def is_active(self):
        return self.actual_return_date is None or self.actual_return_date > date.today()

    def __str__(self):
        return f"Borrowing {self.book.title}"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "P", "Pending"
        PAID = "A", "Paid"

    class Type(models.TextChoices):
        PAYMENT = "P", "Payment"
        FINE = "F", "Fine"

    status = models.CharField(
        choices=Status.choices, default=Status.PENDING, max_length=1
    )
    type = models.CharField(choices=Type.choices, max_length=1)
    borrowing_id = models.ForeignKey(
        "Borrowing", on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=100)
    money_to_pay = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.type} {self.borrowing_id}"
