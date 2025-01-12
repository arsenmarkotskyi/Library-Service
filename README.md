# Library-Service

The `Library-Service` API is a Django-based project for managing a library system. It includes features like managing books, users, borrowings, and payments, as well as sending notifications via Telegram and integrating Stripe for payment processing.

## Tasks

## Table of Contents
1. [CRUD functionality for the Books Service](#1-implement-the-crud-functionality-for-the-books-service)
2. [Add permissions to the Books Service](#2-add-permissions-to-the-books-service)
3. [Implement CRUD for the Users Service](#3-implement-crud-for-the-users-service)
4. [Implement the serializer & views for all the endpoints](#4-implement-the-serializer--views-for-all-the-endpoints)
5. [Implement the Create Borrowing endpoint](#5-implement-the-create-borrowing-endpoint)
6. [Add filtering for the Borrowings List endpoint](#6-add-filtering-for-the-borrowings-list-endpoint)
7. [Implement a return Borrowing functionality](#7-implement-a-return-borrowing-functionality)
8. [Implement the possibility of sending notifications on each Borrowing creation](#8-implement-the-possibility-of-sending-notifications-on-each-borrowing-creation)
9. [Implement a daily function for checking overdue borrowings](#9-implement-a-daily-function-for-checking-overdue-borrowings)
10. [Create your first Stripe Payment Session](#10-create-your-first-stripe-payment-session)

## 1) Implement the CRUD functionality for the Books Service
- **Initialize the books app**: Set up the `books` app to manage book-related functionality.
- **Add the book model**: Create the `Book` model to represent books in the library.
- **Implement the serializer & views**: Develop serializers and views to handle all CRUD operations for books (create, read, update, delete).

---

## 2) Add permissions to the Books Service
- **Admin Permissions**: Only admin users should have the ability to create, update, or delete books.
- **Public Access for Listing Books**: Allow all users (even unauthenticated ones) to view the list of books.
- **JWT Authentication**: Use JWT token authentication for securing access to book management endpoints.

---

## 3) Implement CRUD for the Users Service
- **Initialize the users app**: Set up the `users` app to manage user-related functionality.
- **Add the user model**: Extend the `AbstractUser` model to include email support and other necessary fields.
- **JWT Support**: Implement JWT-based authentication for user login and registration.
- **ModHeader Integration**: Modify the default `Authorization` header to `Authorize` for a better experience with the `ModHeader` Chrome extension. Consult the documentation for detailed implementation.

---

## 4) Implement the serializer & views for all the endpoints
- **Borrowing List & Detail Endpoints**: Implement endpoints for listing all borrowings and retrieving details about individual borrowings.
- **Initialize the borrowings app**: Create the `borrowings` app to handle borrowing-related functionality.
- **Add Borrowing Model**: Create the `Borrowing` model with constraints like `borrow_date`, `expected_return_date`, and `actual_return_date`.
- **Implement the serializer**: Design a read serializer that includes detailed information about the borrowed books.
- **Create List & Detail Views**: Develop views to handle listing borrowings and retrieving detailed information.

---

## 5) Implement the Create Borrowing endpoint
- **Create Borrowing Serializer**: Build a serializer to handle creating borrowings.
- **Inventory Validation**: Ensure that a book’s inventory is greater than 0 before allowing it to be borrowed.
- **Decrease Inventory**: Deduct 1 from the book's inventory when a borrowing is created.
- **User Association**: Attach the current authenticated user to the borrowing record.
- **Create the Endpoint**: Implement the endpoint for creating a new borrowing.

---

## 6) Add filtering for the Borrowings List endpoint
- **User-specific Borrowings**: Ensure that non-admin users can only see their own borrowings.
- **Authenticated Access**: Restrict access to borrowings to authenticated users only.
- **Active Borrowings Filter**: Add the `is_active` parameter to filter borrowings that are still active (i.e., not returned).
- **Admin Filtering by User**: Allow admins to view borrowings for a specific user by adding a `user_id` parameter.

---

## 7) Implement a Return Borrowing functionality
- **Prevent Double Returns**: Ensure that a book can’t be returned twice.
- **Update Inventory**: Add 1 to the book's inventory when it is returned.
- **Create the Endpoint**: Develop an endpoint for returning borrowings.

---

## 8) Implement the possibility of sending notifications on each Borrowing creation
- **Telegram Chat Setup**: Create a Telegram chat where notifications will be posted.
- **Telegram Bot Setup**: Configure a Telegram bot to send notifications.
- **SendMessage Interface**: Investigate the `sendMessage` function of the Telegram API for sending messages.
- **Privacy Considerations**: Use `python-dotenv` to manage private data and ensure sensitive information is not exposed (e.g., in GitHub).
- **Message Helper**: Create a helper function for sending notifications to the Telegram chat.
- **Integrate Notifications**: Send a notification on Telegram every time a new borrowing is created, including relevant details.

---

## 9) Implement a daily function for checking overdue borrowings
- **Overdue Borrowings**: Filter borrowings that are overdue (i.e., `expected_return_date` is today or earlier, and the book is not yet returned).
- **Telegram Notifications for Overdue Books**: Send detailed notifications about each overdue borrowing to the Telegram chat.
- **Scheduled Task**: Use **Django-Q** or **Django-Celery** to create a scheduled task that runs daily to check for overdue borrowings.
- **No Overdue Borrowings Notification**: If there are no overdue borrowings for a specific day, send a notification saying "No borrowings overdue today!"

---

## 10) Create your first Stripe Payment Session
- **Understand Stripe Documentation**: Dive into Stripe's documentation to learn how to work with payments and sessions.
- **Set Up Stripe Account**: Create a Stripe test account and use only test data (no real money transactions).
- **Stripe Test Session**: Create a test Stripe payment session using the documentation (you can use the Flask example as a reference).
- **Manual Payments in the Library System**: Manually create 1-2 payments and attach the `session_url` and `session_id` to each payment.
- **Test Payment Endpoints**: Ensure that the payment list and detail endpoints work correctly.
- **No Frontend Required**: This task is entirely backend-focused, and no frontend implementation is needed.

---


## Requirements

- Python 3.8 or later
- Django 3.x or later
- Stripe account (for payment handling)
- Telegram bot and chat setup for notifications
- Python-dotenv for managing environment variables

## Setup

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/arsenmarkotskyi/Library-Service
cd library-service
python -m venv env
source env/bin/activate   # On Windows use: env\Scripts\activate
pip install -r requirements.txt
```

### Create a .env file in the root directory with the following environment variables:

STRIPE_SECRET_KEY=your_stripe_secret_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

You can refer to the .env.sample file for an example.

## Apply Migrations
Run the following command to apply the database migrations:

```bash
python manage.py migrate
```

## Create a Superuser
Create a superuser to manage the application through the Django admin interface:

```bash
python manage.py createsuperuser
```

## Start the Server
Run the Django development server:

```bash
python manage.py runserver
```
You can now access the application at http://127.0.0.1:8000/.

## Testing
To ensure everything is working correctly, run the tests with:

```bash
python manage.py test
```






